from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import json
from app.models.abac import Policy, PolicyAssignment, AttributeValue, AccessDecisionLog
from app.core.config import settings
from app.services.security import SecurityService
from app.core.cache import redis_client

class ABACService:
    def __init__(self, db: Session):
        self.db = db
        self.security_service = SecurityService(db)
        self.cache_ttl = 300  # 5 minutes cache TTL

    async def evaluate_access(
        self,
        user_id: int,
        resource_id: str,
        resource_type: str,
        action: str,
        context: Dict[str, Any]
    ) -> bool:
        """
        Evaluate access based on ABAC policies and context.
        """
        # Get user attributes
        user_attributes = await self._get_user_attributes(user_id)
        
        # Get resource attributes
        resource_attributes = await self._get_resource_attributes(resource_id, resource_type)
        
        # Get environment attributes
        env_attributes = await self._get_environment_attributes(context)
        
        # Combine all attributes
        evaluation_context = {
            "user": user_attributes,
            "resource": resource_attributes,
            "environment": env_attributes,
            "action": action
        }

        # Check cache first
        cache_key = f"abac:decision:{user_id}:{resource_id}:{action}"
        cached_decision = await redis_client.get(cache_key)
        if cached_decision:
            return json.loads(cached_decision)

        # Get applicable policies
        policies = await self._get_applicable_policies(resource_id, resource_type)
        
        # Evaluate policies in order of priority
        for policy in sorted(policies, key=lambda x: x.priority, reverse=True):
            decision = await self._evaluate_policy(policy, evaluation_context)
            if decision is not None:
                # Cache the decision
                await redis_client.setex(
                    cache_key,
                    self.cache_ttl,
                    json.dumps(decision)
                )
                
                # Log the decision
                await self._log_access_decision(
                    user_id,
                    resource_id,
                    resource_type,
                    action,
                    decision,
                    policy.id,
                    evaluation_context
                )
                
                return decision

        # Default deny
        await self._log_access_decision(
            user_id,
            resource_id,
            resource_type,
            action,
            False,
            None,
            evaluation_context
        )
        return False

    async def _get_user_attributes(self, user_id: int) -> Dict[str, Any]:
        """Get user attributes from the database."""
        attributes = self.db.query(AttributeValue).filter(
            AttributeValue.entity_id == str(user_id),
            AttributeValue.entity_type == "user",
            AttributeValue.expires_at > datetime.utcnow()
        ).all()
        
        return {attr.attribute.name: attr.value for attr in attributes}

    async def _get_resource_attributes(self, resource_id: str, resource_type: str) -> Dict[str, Any]:
        """Get resource attributes from the database."""
        attributes = self.db.query(AttributeValue).filter(
            AttributeValue.entity_id == resource_id,
            AttributeValue.entity_type == resource_type,
            AttributeValue.expires_at > datetime.utcnow()
        ).all()
        
        return {attr.attribute.name: attr.value for attr in attributes}

    async def _get_environment_attributes(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get environment attributes from context and system."""
        env_attributes = {
            "time": datetime.utcnow().isoformat(),
            "ip": context.get("ip_address"),
            "user_agent": context.get("user_agent"),
            "location": context.get("location"),
            "device_info": context.get("device_info")
        }
        
        # Add any additional environment attributes
        if "environment" in context:
            env_attributes.update(context["environment"])
            
        return env_attributes

    async def _get_applicable_policies(self, resource_id: str, resource_type: str) -> List[Policy]:
        """Get all applicable policies for a resource."""
        assignments = self.db.query(PolicyAssignment).filter(
            PolicyAssignment.resource_id == resource_id,
            PolicyAssignment.resource_type == resource_type,
            PolicyAssignment.is_active == True,
            PolicyAssignment.expires_at > datetime.utcnow()
        ).all()
        
        policy_ids = [assignment.policy_id for assignment in assignments]
        return self.db.query(Policy).filter(
            Policy.id.in_(policy_ids),
            Policy.is_active == True
        ).all()

    async def _evaluate_policy(self, policy: Policy, context: Dict[str, Any]) -> Optional[bool]:
        """Evaluate a single policy against the context."""
        try:
            # Evaluate conditions using a simple expression evaluator
            # This is a basic implementation - you might want to use a more robust solution
            conditions = policy.conditions
            result = self._evaluate_conditions(conditions, context)
            
            return result if policy.effect == "allow" else not result
            
        except Exception as e:
            # Log the error and continue with other policies
            print(f"Error evaluating policy {policy.id}: {str(e)}")
            return None

    def _evaluate_conditions(self, conditions: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate policy conditions against the context."""
        if not conditions:
            return True
            
        for key, value in conditions.items():
            if key not in context:
                return False
                
            if isinstance(value, dict):
                if not self._evaluate_condition_dict(value, context[key]):
                    return False
            elif value != context[key]:
                return False
                
        return True

    def _evaluate_condition_dict(self, condition: Dict[str, Any], value: Any) -> bool:
        """Evaluate a condition dictionary against a value."""
        for op, expected in condition.items():
            if op == "equals":
                if value != expected:
                    return False
            elif op == "not_equals":
                if value == expected:
                    return False
            elif op == "contains":
                if expected not in value:
                    return False
            elif op == "in":
                if value not in expected:
                    return False
            elif op == "greater_than":
                if value <= expected:
                    return False
            elif op == "less_than":
                if value >= expected:
                    return False
            elif op == "regex":
                import re
                if not re.match(expected, str(value)):
                    return False
            else:
                raise ValueError(f"Unsupported operator: {op}")
                
        return True

    async def _log_access_decision(
        self,
        user_id: int,
        resource_id: str,
        resource_type: str,
        action: str,
        decision: bool,
        policy_id: Optional[int],
        context: Dict[str, Any]
    ) -> None:
        """Log access decision details."""
        log_entry = AccessDecisionLog(
            user_id=user_id,
            resource_id=resource_id,
            resource_type=resource_type,
            action=action,
            decision="allow" if decision else "deny",
            policy_id=policy_id,
            evaluation_context=context,
            evaluation_result={"decision": decision},
            ip_address=context.get("ip_address"),
            user_agent=context.get("user_agent"),
            location=context.get("location"),
            device_info=context.get("device_info")
        )
        
        self.db.add(log_entry)
        self.db.commit() 
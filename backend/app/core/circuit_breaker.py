from typing import Any, Callable, Optional, Dict
import time
from enum import Enum
import logging
from functools import wraps
from app.core.config import settings

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "CLOSED"  # Normal operation
    OPEN = "OPEN"      # Failing, reject requests
    HALF_OPEN = "HALF_OPEN"  # Testing if service recovered

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = settings.CIRCUIT_BREAKER_FAILURE_THRESHOLD,
        recovery_timeout: int = settings.CIRCUIT_BREAKER_RECOVERY_TIMEOUT,
        name: str = "default"
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self.last_success_time = 0
        self._circuits: Dict[str, "CircuitBreaker"] = {}

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not settings.ENABLE_CIRCUIT_BREAKER:
                return await func(*args, **kwargs)

            if self.state == CircuitState.OPEN:
                if time.time() - self.last_failure_time >= self.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                    logger.info(f"Circuit breaker {self.name} moved to HALF_OPEN state")
                else:
                    logger.warning(f"Circuit breaker {self.name} is OPEN, request rejected")
                    raise Exception(f"Circuit breaker {self.name} is OPEN")

            try:
                result = await func(*args, **kwargs)
                self._handle_success()
                return result
            except Exception as e:
                self._handle_failure()
                raise e

        return wrapper

    def _handle_success(self) -> None:
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.last_success_time = time.time()
            logger.info(f"Circuit breaker {self.name} moved to CLOSED state")
        elif self.state == CircuitState.CLOSED:
            self.last_success_time = time.time()

    def _handle_failure(self) -> None:
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(
                f"Circuit breaker {self.name} moved to OPEN state after {self.failure_count} failures"
            )

    @classmethod
    def get_circuit(cls, name: str) -> "CircuitBreaker":
        if name not in cls._circuits:
            cls._circuits[name] = CircuitBreaker(name=name)
        return cls._circuits[name]

    def get_state(self) -> CircuitState:
        return self.state

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time,
            "last_success_time": self.last_success_time,
            "failure_threshold": self.failure_threshold,
            "recovery_timeout": self.recovery_timeout
        }

# Example usage:
# @CircuitBreaker.get_circuit("database")
# async def database_operation():
#     # Your database operation here
#     pass 
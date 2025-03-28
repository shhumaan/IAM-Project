from typing import Any, Callable, Dict, List, Optional
import asyncio
import logging
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from app.core.config import settings

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

@dataclass
class Task:
    id: str
    name: str
    func: Callable
    args: tuple
    kwargs: dict
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    result: Any = None

class TaskManager:
    def __init__(
        self,
        max_tasks: int = settings.MAX_BACKGROUND_TASKS,
        task_timeout: int = settings.BACKGROUND_TASK_TIMEOUT,
        queue_size: int = settings.TASK_QUEUE_SIZE
    ):
        self.max_tasks = max_tasks
        self.task_timeout = task_timeout
        self.queue_size = queue_size
        self.tasks: Dict[str, Task] = {}
        self.running_tasks: List[str] = []
        self.task_queue: asyncio.Queue = asyncio.Queue(maxsize=queue_size)
        self._task_counter = 0
        self._lock = asyncio.Lock()
        self._running = False

    async def start(self) -> None:
        """Start the task manager and begin processing tasks."""
        if not settings.ENABLE_BACKGROUND_TASKS:
            logger.warning("Background tasks are disabled")
            return

        self._running = True
        asyncio.create_task(self._process_tasks())
        logger.info("Task manager started")

    async def stop(self) -> None:
        """Stop the task manager and cancel all running tasks."""
        self._running = False
        for task_id in self.running_tasks:
            await self.cancel_task(task_id)
        logger.info("Task manager stopped")

    async def submit_task(
        self,
        func: Callable,
        *args: Any,
        name: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        """Submit a new task to be executed in the background."""
        async with self._lock:
            self._task_counter += 1
            task_id = f"task_{self._task_counter}"
            
            if name is None:
                name = func.__name__

            task = Task(
                id=task_id,
                name=name,
                func=func,
                args=args,
                kwargs=kwargs,
                status=TaskStatus.PENDING,
                created_at=datetime.utcnow()
            )

            self.tasks[task_id] = task
            await self.task_queue.put(task_id)
            logger.info(f"Task {task_id} ({name}) submitted")
            return task_id

    async def get_task_status(self, task_id: str) -> Optional[Task]:
        """Get the current status of a task."""
        return self.tasks.get(task_id)

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task."""
        if task_id in self.running_tasks:
            self.running_tasks.remove(task_id)
            self.tasks[task_id].status = TaskStatus.CANCELLED
            self.tasks[task_id].completed_at = datetime.utcnow()
            logger.info(f"Task {task_id} cancelled")
            return True
        return False

    async def _process_tasks(self) -> None:
        """Process tasks from the queue."""
        while self._running:
            try:
                if len(self.running_tasks) >= self.max_tasks:
                    await asyncio.sleep(1)
                    continue

                task_id = await self.task_queue.get()
                task = self.tasks[task_id]

                if task.status == TaskStatus.CANCELLED:
                    continue

                self.running_tasks.append(task_id)
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.utcnow()

                try:
                    result = await asyncio.wait_for(
                        task.func(*task.args, **task.kwargs),
                        timeout=self.task_timeout
                    )
                    task.status = TaskStatus.COMPLETED
                    task.result = result
                except asyncio.TimeoutError:
                    task.status = TaskStatus.FAILED
                    task.error = "Task timed out"
                except Exception as e:
                    task.status = TaskStatus.FAILED
                    task.error = str(e)
                finally:
                    task.completed_at = datetime.utcnow()
                    self.running_tasks.remove(task_id)

            except Exception as e:
                logger.error(f"Error processing task: {str(e)}")
                await asyncio.sleep(1)

    def get_metrics(self) -> Dict[str, Any]:
        """Get current task manager metrics."""
        return {
            "total_tasks": len(self.tasks),
            "running_tasks": len(self.running_tasks),
            "queue_size": self.task_queue.qsize(),
            "max_tasks": self.max_tasks,
            "task_timeout": self.task_timeout,
            "queue_size_limit": self.queue_size
        }

# Create a global task manager instance
task_manager = TaskManager()

# Example usage:
# async def example_task():
#     await asyncio.sleep(5)
#     return "Task completed"
#
# # Submit a task
# task_id = await task_manager.submit_task(example_task, name="example")
#
# # Check task status
# task = await task_manager.get_task_status(task_id)
# if task.status == TaskStatus.COMPLETED:
#     print(f"Task result: {task.result}") 
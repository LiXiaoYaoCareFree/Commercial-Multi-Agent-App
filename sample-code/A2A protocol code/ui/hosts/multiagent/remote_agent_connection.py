from typing import Union
from a2a.types import Task, TaskStatusUpdateEvent, TaskArtifactUpdateEvent

TaskCallbackArg = Union[Task, TaskStatusUpdateEvent, TaskArtifactUpdateEvent]

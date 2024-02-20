from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date

from todoist_api_python import models
from todoist_api_python.api import TodoistAPI

from app.config import TODOIST_API_KEY


@dataclass
class TodoistTask:
    summary: str
    description: str
    priority: int
    order: int
    due_date: date
    due_time: datetime | None = None

    @staticmethod
    def model_to_task(task_model: models.Task) -> TodoistTask:
        return TodoistTask(
            summary=task_model.content,
            description=task_model.description,
            priority=task_model.priority,
            order=task_model.order,
            due_date=datetime.strptime(task_model.due.date, '%Y-%m-%d').date(),
            due_time=datetime.strptime(task_model.due.datetime, '%Y-%m-%dT%H:%M:%S') if task_model.due.datetime else None,
        )


class Todoist:
    def __init__(self):
        self._api = TodoistAPI(TODOIST_API_KEY)

    def get_next_tasks(self) -> list[TodoistTask]:
        next_tasks_filter = 'due: today|tomorrow'
        return self.__get_tasks_by_filter(next_tasks_filter)

    def __get_tasks_by_filter(self, todoist_filter: str) -> list[TodoistTask]:
        task_models = self._api.get_tasks(filter=todoist_filter)
        tasks = list(map(TodoistTask.model_to_task, task_models))

        # Sort by: due date, if it has a due time, priority (descending), order
        sorted_tasks = sorted(tasks, key=lambda task: (
            task.due_date,
            task.due_time if task.due_time is not None else datetime.max,
            -task.priority,
            task.order))
        return sorted_tasks

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional


@dataclass
class Task:
    name: str
    description: str
    duration: float  # in hours
    priority: int  # 1..5
    complete: bool = False

    def mark_complete(self) -> None:
        self.complete = True

    def update(self, *, name: Optional[str] = None, description: Optional[str] = None,
               duration: Optional[float] = None, priority: Optional[int] = None) -> None:
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if duration is not None:
            self.duration = duration
        if priority is not None:
            self.priority = priority


@dataclass
class Pet:
    name: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def assign_task(self, task: Task) -> None:
        self.tasks.append(task)

    def complete_task(self, task_name: str) -> bool:
        for task in self.tasks:
            if task.name == task_name:
                task.mark_complete()
                return True
        return False

    def remove_task(self, task_name: str) -> bool:
        for i, task in enumerate(self.tasks):
            if task.name == task_name:
                del self.tasks[i]
                return True
        return False


@dataclass
class Owner:
    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def get_pet(self, pet_name: str) -> Optional[Pet]:
        for pet in self.pets:
            if pet.name == pet_name:
                return pet
        return None


@dataclass
class Schedule:
    day: date
    task_list: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.task_list.append(task)

    def generate(self) -> List[Task]:
        # Basic sorted schedule by priority (higher first) then uncompleted first
        return sorted(self.task_list, key=lambda t: (t.complete, -t.priority, t.duration))

    def clear(self) -> None:
        self.task_list.clear()

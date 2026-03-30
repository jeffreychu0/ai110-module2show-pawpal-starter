from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional
from uuid import UUID, uuid4


@dataclass
class Task:
    """A single pet care activity."""
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    duration: float = 0.0        # hours
    priority: int = 1            # 1 (low) .. 5 (high)
    frequency: str = "daily"     # "daily" | "weekly" | "monthly" | "as_needed"
    complete: bool = False

    def mark_complete(self) -> None:
        self.complete = True

    def mark_incomplete(self) -> None:
        self.complete = False

    def update(self, *, name: Optional[str] = None, description: Optional[str] = None,
               duration: Optional[float] = None, priority: Optional[int] = None,
               frequency: Optional[str] = None) -> None:
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if duration is not None:
            self.duration = duration
        if priority is not None:
            self.priority = priority
        if frequency is not None:
            self.frequency = frequency

    def __str__(self) -> str:
        status = "done" if self.complete else "pending"
        return f"[{status}] {self.name} (priority={self.priority}, {self.duration}h, {self.frequency})"


@dataclass
class Pet:
    """A pet with its own list of care tasks."""
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    age: int = 0
    tasks: List[Task] = field(default_factory=list)

    def assign_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def get_task(self, task_id: UUID) -> Optional[Task]:
        """Return the task with the given id, or None."""
        return next((t for t in self.tasks if t.id == task_id), None)

    def complete_task(self, task_id: UUID) -> bool:
        """Mark a task complete. Returns True if the task was found."""
        task = self.get_task(task_id)
        if task:
            task.mark_complete()
            return True
        return False

    def uncomplete_task(self, task_id: UUID) -> bool:
        """Reset a task to incomplete. Returns True if the task was found."""
        task = self.get_task(task_id)
        if task:
            task.mark_incomplete()
            return True
        return False

    def remove_task(self, task_id: UUID) -> bool:
        """Remove a task by id. Returns True if removed."""
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                del self.tasks[i]
                return True
        return False

    @property
    def pending_tasks(self) -> List[Task]:
        """All incomplete tasks for this pet."""
        return [t for t in self.tasks if not t.complete]

    def __str__(self) -> str:
        total = len(self.tasks)
        pending = len(self.pending_tasks)
        return f"{self.name} (age {self.age}) — {pending}/{total} tasks pending"


@dataclass
class Owner:
    """An owner who manages one or more pets."""
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def get_pet(self, pet_id: UUID) -> Optional[Pet]:
        """Return the pet with the given id, or None."""
        return next((p for p in self.pets if p.id == pet_id), None)

    def find_pet_by_name(self, pet_name: str) -> Optional[Pet]:
        """Return the first pet whose name matches (case-sensitive), or None."""
        return next((p for p in self.pets if p.name == pet_name), None)

    def remove_pet(self, pet_id: UUID) -> bool:
        """Remove a pet by id. Returns True if removed."""
        for i, pet in enumerate(self.pets):
            if pet.id == pet_id:
                del self.pets[i]
                return True
        return False

    def all_tasks(self) -> List[Task]:
        """Aggregate every task across all pets."""
        return [task for pet in self.pets for task in pet.tasks]

    def all_pending_tasks(self) -> List[Task]:
        """Aggregate every incomplete task across all pets."""
        return [task for pet in self.pets for task in pet.pending_tasks]

    def __str__(self) -> str:
        return f"Owner: {self.name} — {len(self.pets)} pet(s)"


@dataclass
class Schedule:
    """A single-day view of tasks, sorted for execution."""
    day: date
    task_list: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.task_list.append(task)

    def remove_task(self, task_id: UUID) -> bool:
        for i, task in enumerate(self.task_list):
            if task.id == task_id:
                del self.task_list[i]
                return True
        return False

    def generate(self) -> List[Task]:
        """Return tasks sorted: incomplete first, then by descending priority, then duration."""
        return sorted(self.task_list, key=lambda t: (t.complete, -t.priority, t.duration))

    def clear(self) -> None:
        self.task_list.clear()

    def __str__(self) -> str:
        lines = [f"Schedule for {self.day} ({len(self.task_list)} tasks):"]
        for task in self.generate():
            lines.append(f"  {task}")
        return "\n".join(lines)


@dataclass
class Scheduler:
    """
    The 'Brain' of PawPal+.

    Sits on top of an Owner and provides cross-pet task retrieval,
    filtering, and schedule generation.
    """
    owner: Owner

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def get_all_tasks(self) -> List[Task]:
        """Return every task across all of the owner's pets."""
        return self.owner.all_tasks()

    def get_pending_tasks(self) -> List[Task]:
        """Return all incomplete tasks across all pets."""
        return self.owner.all_pending_tasks()

    def get_tasks_for_pet(self, pet_id: UUID) -> List[Task]:
        """Return all tasks belonging to a specific pet."""
        pet = self.owner.get_pet(pet_id)
        return pet.tasks if pet else []

    # ------------------------------------------------------------------
    # Filtering / organisation
    # ------------------------------------------------------------------

    def get_tasks_by_priority(self, min_priority: int = 1) -> List[Task]:
        """Return pending tasks at or above min_priority, highest priority first."""
        return sorted(
            [t for t in self.get_pending_tasks() if t.priority >= min_priority],
            key=lambda t: -t.priority,
        )

    def get_tasks_by_frequency(self, frequency: str) -> List[Task]:
        """Return all tasks matching the given frequency string."""
        return [t for t in self.get_all_tasks() if t.frequency == frequency]

    # ------------------------------------------------------------------
    # Schedule building
    # ------------------------------------------------------------------

    def build_schedule(self, day: date) -> Schedule:
        """
        Build a Schedule for *day* from all pending tasks.

        Only tasks that are relevant to the given day are included:
        - 'daily'    → always included
        - 'weekly'   → included if the day's weekday matches today's weekday
        - 'monthly'  → included if the day-of-month matches today's day
        - 'as_needed'→ included only when still pending (incomplete)
        """
        schedule = Schedule(day=day)
        for task in self.get_pending_tasks():
            if task.frequency == "daily":
                schedule.add_task(task)
            elif task.frequency == "weekly" and day.weekday() == date.today().weekday():
                schedule.add_task(task)
            elif task.frequency == "monthly" and day.day == date.today().day:
                schedule.add_task(task)
            elif task.frequency == "as_needed":
                schedule.add_task(task)
        return schedule

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def summary(self) -> str:
        """Print a quick status overview for all pets."""
        lines = [f"=== PawPal+ Summary for {self.owner.name} ==="]
        for pet in self.owner.pets:
            lines.append(f"  {pet}")
            for task in pet.tasks:
                lines.append(f"    {task}")
        total = len(self.get_all_tasks())
        pending = len(self.get_pending_tasks())
        lines.append(f"Total: {pending} pending / {total} tasks")
        return "\n".join(lines)

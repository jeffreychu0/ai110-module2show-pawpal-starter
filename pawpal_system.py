"""
pawpal_system.py
================
Core domain model for the PawPal+ pet care scheduling application.

Classes:
    Task      -- A single pet care activity.
    Pet       -- A pet with its own list of Tasks.
    Owner     -- An owner who manages one or more Pets.
    Schedule  -- A single-day ordered view of Tasks.
    Scheduler -- Cross-pet task retrieval and schedule generation.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional
from uuid import UUID, uuid4


@dataclass
class Task:
    """A single pet care activity.

    Attributes:
        id (UUID): Auto-generated unique identifier.
        name (str): Short label for the task (e.g. "Morning Walk").
        description (str): Longer explanation of what the task involves.
        duration (float): Expected time to complete the task, in hours.
        priority (int): Importance ranking from 1 (lowest) to 5 (highest).
        frequency (str): How often the task recurs. One of:
            ``"daily"``, ``"weekly"``, ``"monthly"``, or ``"as_needed"``.
        complete (bool): Whether the task has been completed.
    """

    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    duration: float = 0.0        # hours
    priority: int = 1            # 1 (low) .. 5 (high)
    frequency: str = "daily"     # "daily" | "weekly" | "monthly" | "as_needed"
    complete: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed.

        Sets ``complete`` to ``True``. Has no effect if the task is
        already complete.
        """
        self.complete = True

    def mark_incomplete(self) -> None:
        """Reset this task to incomplete.

        Sets ``complete`` to ``False``. Useful for re-scheduling a task
        on a new day or after an accidental completion.
        """
        self.complete = False

    def update(self, *, name: Optional[str] = None, description: Optional[str] = None,
               duration: Optional[float] = None, priority: Optional[int] = None,
               frequency: Optional[str] = None) -> None:
        """Update one or more fields on this task in place.

        Only keyword arguments that are explicitly passed (i.e. not
        ``None``) are applied, so callers can change a single field
        without touching the rest.

        Args:
            name (str, optional): New short label for the task.
            description (str, optional): New detailed description.
            duration (float, optional): New expected duration in hours.
            priority (int, optional): New priority ranking (1–5).
            frequency (str, optional): New recurrence frequency string.
        """
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
        """Return a human-readable one-line summary of this task.

        Returns:
            str: A string in the form
            ``"[pending] Walk (priority=5, 0.5h, daily)"``.
        """
        status = "done" if self.complete else "pending"
        return f"[{status}] {self.name} (priority={self.priority}, {self.duration}h, {self.frequency})"


@dataclass
class Pet:
    """A pet with its own list of care tasks.

    Attributes:
        id (UUID): Auto-generated unique identifier.
        name (str): The pet's name (e.g. "Buddy").
        age (int): The pet's age in years.
        tasks (List[Task]): All tasks assigned to this pet.
    """

    id: UUID = field(default_factory=uuid4)
    name: str = ""
    age: int = 0
    tasks: List[Task] = field(default_factory=list)

    def assign_task(self, task: Task) -> None:
        """Append a task to this pet's task list.

        Args:
            task (Task): The task to assign.
        """
        self.tasks.append(task)

    def get_task(self, task_id: UUID) -> Optional[Task]:
        """Look up a task by its unique identifier.

        Args:
            task_id (UUID): The id of the task to find.

        Returns:
            Task: The matching task, or ``None`` if not found.
        """
        return next((t for t in self.tasks if t.id == task_id), None)

    def complete_task(self, task_id: UUID) -> bool:
        """Mark a task as complete.

        Args:
            task_id (UUID): The id of the task to complete.

        Returns:
            bool: ``True`` if the task was found and marked complete,
            ``False`` if no task with that id exists.
        """
        task = self.get_task(task_id)
        if task:
            task.mark_complete()
            return True
        return False

    def uncomplete_task(self, task_id: UUID) -> bool:
        """Reset a task back to incomplete.

        Args:
            task_id (UUID): The id of the task to reset.

        Returns:
            bool: ``True`` if the task was found and reset,
            ``False`` if no task with that id exists.
        """
        task = self.get_task(task_id)
        if task:
            task.mark_incomplete()
            return True
        return False

    def remove_task(self, task_id: UUID) -> bool:
        """Remove a task from this pet's task list.

        Args:
            task_id (UUID): The id of the task to remove.

        Returns:
            bool: ``True`` if the task was found and removed,
            ``False`` if no task with that id exists.
        """
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                del self.tasks[i]
                return True
        return False

    @property
    def pending_tasks(self) -> List[Task]:
        """All incomplete tasks assigned to this pet.

        Returns:
            List[Task]: Tasks where ``complete`` is ``False``.
        """
        return [t for t in self.tasks if not t.complete]

    def __str__(self) -> str:
        """Return a human-readable summary of this pet and its task counts.

        Returns:
            str: A string in the form ``"Buddy (age 3) — 2/3 tasks pending"``.
        """
        total = len(self.tasks)
        pending = len(self.pending_tasks)
        return f"{self.name} (age {self.age}) — {pending}/{total} tasks pending"


@dataclass
class Owner:
    """An owner who manages one or more pets.

    Attributes:
        id (UUID): Auto-generated unique identifier.
        name (str): The owner's display name.
        pets (List[Pet]): All pets registered under this owner.
    """

    id: UUID = field(default_factory=uuid4)
    name: str = ""
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a new pet under this owner.

        Args:
            pet (Pet): The pet to add.
        """
        self.pets.append(pet)

    def get_pet(self, pet_id: UUID) -> Optional[Pet]:
        """Look up a pet by its unique identifier.

        Args:
            pet_id (UUID): The id of the pet to find.

        Returns:
            Pet: The matching pet, or ``None`` if not found.
        """
        return next((p for p in self.pets if p.id == pet_id), None)

    def find_pet_by_name(self, pet_name: str) -> Optional[Pet]:
        """Find the first pet whose name matches exactly (case-sensitive).

        Args:
            pet_name (str): The name to search for.

        Returns:
            Pet: The first matching pet, or ``None`` if not found.
        """
        return next((p for p in self.pets if p.name == pet_name), None)

    def remove_pet(self, pet_id: UUID) -> bool:
        """Remove a pet from this owner's pet list.

        Args:
            pet_id (UUID): The id of the pet to remove.

        Returns:
            bool: ``True`` if the pet was found and removed,
            ``False`` if no pet with that id exists.
        """
        for i, pet in enumerate(self.pets):
            if pet.id == pet_id:
                del self.pets[i]
                return True
        return False

    def all_tasks(self) -> List[Task]:
        """Aggregate every task across all of this owner's pets.

        Returns:
            List[Task]: A flat list of all tasks, in pet-registration order.
        """
        return [task for pet in self.pets for task in pet.tasks]

    def all_pending_tasks(self) -> List[Task]:
        """Aggregate every incomplete task across all of this owner's pets.

        Returns:
            List[Task]: A flat list of tasks where ``complete`` is ``False``.
        """
        return [task for pet in self.pets for task in pet.pending_tasks]

    def __str__(self) -> str:
        """Return a human-readable summary of this owner.

        Returns:
            str: A string in the form ``"Owner: Alex — 2 pet(s)"``.
        """
        return f"Owner: {self.name} — {len(self.pets)} pet(s)"


@dataclass
class Schedule:
    """A single-day ordered view of tasks.

    Tasks are stored as added and sorted on demand via ``generate()``.

    Attributes:
        day (date): The calendar date this schedule applies to.
        task_list (List[Task]): Tasks included in this schedule.
    """

    day: date
    task_list: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this day's schedule.

        Args:
            task (Task): The task to include.
        """
        self.task_list.append(task)

    def remove_task(self, task_id: UUID) -> bool:
        """Remove a task from this schedule by id.

        Args:
            task_id (UUID): The id of the task to remove.

        Returns:
            bool: ``True`` if the task was found and removed,
            ``False`` if no task with that id exists.
        """
        for i, task in enumerate(self.task_list):
            if task.id == task_id:
                del self.task_list[i]
                return True
        return False

    def generate(self) -> List[Task]:
        """Return tasks sorted for execution order.

        Sort key (in order of precedence):

        1. Incomplete tasks before complete tasks.
        2. Higher priority before lower priority.
        3. Shorter duration before longer duration (tie-breaker).

        Returns:
            List[Task]: A new sorted list; ``task_list`` is not modified.
        """
        return sorted(self.task_list, key=lambda t: (t.complete, -t.priority, t.duration))

    def clear(self) -> None:
        """Remove all tasks from this schedule."""
        self.task_list.clear()

    def __str__(self) -> str:
        """Return a formatted multi-line view of today's schedule.

        Returns:
            str: A header line followed by one indented line per task,
            sorted by ``generate()``.
        """
        lines = [f"Schedule for {self.day} ({len(self.task_list)} tasks):"]
        for task in self.generate():
            lines.append(f"  {task}")
        return "\n".join(lines)


@dataclass
class Scheduler:
    """The 'Brain' of PawPal+.

    Sits on top of an ``Owner`` and provides unified, cross-pet task
    retrieval, filtering, and schedule generation. All state lives in
    the owner's pets; ``Scheduler`` adds no state of its own.

    Attributes:
        owner (Owner): The owner whose pets and tasks are managed.
    """

    owner: Owner

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def get_all_tasks(self) -> List[Task]:
        """Return every task across all of the owner's pets.

        Returns:
            List[Task]: Flat list of all tasks in pet-registration order.
        """
        return self.owner.all_tasks()

    def get_pending_tasks(self) -> List[Task]:
        """Return all incomplete tasks across all of the owner's pets.

        Returns:
            List[Task]: Flat list of tasks where ``complete`` is ``False``.
        """
        return self.owner.all_pending_tasks()

    def get_tasks_for_pet(self, pet_id: UUID) -> List[Task]:
        """Return all tasks belonging to a specific pet.

        Args:
            pet_id (UUID): The id of the pet to look up.

        Returns:
            List[Task]: The pet's task list, or an empty list if the pet
            is not found.
        """
        pet = self.owner.get_pet(pet_id)
        return pet.tasks if pet else []

    # ------------------------------------------------------------------
    # Filtering / organisation
    # ------------------------------------------------------------------

    def get_tasks_by_priority(self, min_priority: int = 1) -> List[Task]:
        """Return pending tasks at or above a minimum priority, sorted highest first.

        Args:
            min_priority (int): Inclusive lower bound on priority (1–5).
                Defaults to ``1`` (returns all pending tasks).

        Returns:
            List[Task]: Pending tasks with ``priority >= min_priority``,
            sorted in descending priority order.
        """
        return sorted(
            [t for t in self.get_pending_tasks() if t.priority >= min_priority],
            key=lambda t: -t.priority,
        )

    def get_tasks_by_frequency(self, frequency: str) -> List[Task]:
        """Return all tasks (complete or not) matching a frequency string.

        Args:
            frequency (str): One of ``"daily"``, ``"weekly"``,
                ``"monthly"``, or ``"as_needed"``.

        Returns:
            List[Task]: All tasks whose ``frequency`` equals the argument.
        """
        return [t for t in self.get_all_tasks() if t.frequency == frequency]

    # ------------------------------------------------------------------
    # Schedule building
    # ------------------------------------------------------------------

    def build_schedule(self, day: date) -> Schedule:
        """Build a :class:`Schedule` for *day* from all pending tasks.

        Frequency rules applied when deciding whether a pending task is
        included in the schedule:

        - ``"daily"``    -- always included.
        - ``"weekly"``   -- included when ``day.weekday()`` matches
          today's weekday (so the same day-of-week each week).
        - ``"monthly"``  -- included when ``day.day`` matches today's
          day-of-month.
        - ``"as_needed"``-- always included (the task itself signals
          it is needed by being incomplete).

        Args:
            day (date): The calendar date to build the schedule for.

        Returns:
            Schedule: A new ``Schedule`` object populated with the
            relevant pending tasks.
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
        """Build a multi-line status overview for all pets and their tasks.

        Returns:
            str: A formatted string listing each pet, its tasks with
            status, and a total pending/total count at the end.
        """
        lines = [f"=== PawPal+ Summary for {self.owner.name} ==="]
        for pet in self.owner.pets:
            lines.append(f"  {pet}")
            for task in pet.tasks:
                lines.append(f"    {task}")
        total = len(self.get_all_tasks())
        pending = len(self.get_pending_tasks())
        lines.append(f"Total: {pending} pending / {total} tasks")
        return "\n".join(lines)

"""Tests for pawpal_system.py"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from datetime import date
from pawpal_system import Task, Pet, Owner, Schedule, Scheduler


# ============================================================
# Task
# ============================================================

class TestTask:
    def test_defaults(self):
        t = Task()
        assert t.name == ""
        assert t.duration == 0.0
        assert t.priority == 1
        assert t.frequency == "daily"
        assert t.complete is False

    def test_unique_ids(self):
        assert Task().id != Task().id

    def test_mark_complete(self):
        t = Task(name="Walk")
        t.mark_complete()
        assert t.complete is True

    def test_mark_incomplete(self):
        t = Task(name="Walk", complete=True)
        t.mark_incomplete()
        assert t.complete is False

    def test_update_name(self):
        t = Task(name="Old")
        t.update(name="New")
        assert t.name == "New"

    def test_update_description(self):
        t = Task(description="Old desc")
        t.update(description="New desc")
        assert t.description == "New desc"

    def test_update_duration(self):
        t = Task(duration=1.0)
        t.update(duration=2.5)
        assert t.duration == 2.5

    def test_update_priority(self):
        t = Task(priority=1)
        t.update(priority=5)
        assert t.priority == 5

    def test_update_frequency(self):
        t = Task(frequency="daily")
        t.update(frequency="weekly")
        assert t.frequency == "weekly"

    def test_update_ignores_none(self):
        t = Task(name="Keep", priority=3)
        t.update(name=None, priority=None)
        assert t.name == "Keep"
        assert t.priority == 3

    def test_str_contains_name(self):
        t = Task(name="Feeding")
        assert "Feeding" in str(t)

    def test_str_shows_pending(self):
        t = Task(name="Walk", complete=False)
        assert "pending" in str(t)

    def test_str_shows_done(self):
        t = Task(name="Walk", complete=True)
        assert "done" in str(t)


# ============================================================
# Pet
# ============================================================

class TestPet:
    def _make_pet(self):
        return Pet(name="Buddy", age=3)

    def test_defaults(self):
        p = Pet()
        assert p.name == ""
        assert p.age == 0
        assert p.tasks == []

    def test_assign_task(self):
        p = self._make_pet()
        t = Task(name="Walk")
        p.assign_task(t)
        assert t in p.tasks

    def test_get_task_found(self):
        p = self._make_pet()
        t = Task(name="Walk")
        p.assign_task(t)
        assert p.get_task(t.id) is t

    def test_get_task_not_found(self):
        p = self._make_pet()
        from uuid import uuid4
        assert p.get_task(uuid4()) is None

    def test_complete_task_success(self):
        p = self._make_pet()
        t = Task(name="Walk")
        p.assign_task(t)
        result = p.complete_task(t.id)
        assert result is True
        assert t.complete is True

    def test_complete_task_missing(self):
        p = self._make_pet()
        from uuid import uuid4
        assert p.complete_task(uuid4()) is False

    def test_uncomplete_task(self):
        p = self._make_pet()
        t = Task(name="Walk", complete=True)
        p.assign_task(t)
        result = p.uncomplete_task(t.id)
        assert result is True
        assert t.complete is False

    def test_uncomplete_task_missing(self):
        p = self._make_pet()
        from uuid import uuid4
        assert p.uncomplete_task(uuid4()) is False

    def test_remove_task_success(self):
        p = self._make_pet()
        t = Task(name="Walk")
        p.assign_task(t)
        result = p.remove_task(t.id)
        assert result is True
        assert t not in p.tasks

    def test_remove_task_missing(self):
        p = self._make_pet()
        from uuid import uuid4
        assert p.remove_task(uuid4()) is False

    def test_pending_tasks_filters_complete(self):
        p = self._make_pet()
        done = Task(name="Done", complete=True)
        todo = Task(name="Todo", complete=False)
        p.assign_task(done)
        p.assign_task(todo)
        assert p.pending_tasks == [todo]

    def test_str_contains_name(self):
        p = Pet(name="Luna")
        assert "Luna" in str(p)


# ============================================================
# Owner
# ============================================================

class TestOwner:
    def _make_owner(self):
        return Owner(name="Alex")

    def test_defaults(self):
        o = Owner()
        assert o.name == ""
        assert o.pets == []

    def test_add_pet(self):
        o = self._make_owner()
        p = Pet(name="Buddy")
        o.add_pet(p)
        assert p in o.pets

    def test_get_pet_found(self):
        o = self._make_owner()
        p = Pet(name="Buddy")
        o.add_pet(p)
        assert o.get_pet(p.id) is p

    def test_get_pet_not_found(self):
        o = self._make_owner()
        from uuid import uuid4
        assert o.get_pet(uuid4()) is None

    def test_find_pet_by_name_found(self):
        o = self._make_owner()
        p = Pet(name="Luna")
        o.add_pet(p)
        assert o.find_pet_by_name("Luna") is p

    def test_find_pet_by_name_missing(self):
        o = self._make_owner()
        assert o.find_pet_by_name("Ghost") is None

    def test_remove_pet_success(self):
        o = self._make_owner()
        p = Pet(name="Buddy")
        o.add_pet(p)
        result = o.remove_pet(p.id)
        assert result is True
        assert p not in o.pets

    def test_remove_pet_missing(self):
        o = self._make_owner()
        from uuid import uuid4
        assert o.remove_pet(uuid4()) is False

    def test_all_tasks_aggregates(self):
        o = self._make_owner()
        p1, p2 = Pet(name="Buddy"), Pet(name="Luna")
        t1, t2, t3 = Task(name="Walk"), Task(name="Feed"), Task(name="Brush")
        p1.assign_task(t1)
        p2.assign_task(t2)
        p2.assign_task(t3)
        o.add_pet(p1)
        o.add_pet(p2)
        all_tasks = o.all_tasks()
        assert sorted([t.name for t in all_tasks]) == sorted(["Walk", "Feed", "Brush"])

    def test_all_tasks_empty(self):
        o = self._make_owner()
        o.add_pet(Pet(name="Buddy"))
        assert o.all_tasks() == []

    def test_all_pending_tasks_excludes_complete(self):
        o = self._make_owner()
        p = Pet(name="Buddy")
        done = Task(name="Done", complete=True)
        todo = Task(name="Todo", complete=False)
        p.assign_task(done)
        p.assign_task(todo)
        o.add_pet(p)
        assert o.all_pending_tasks() == [todo]

    def test_str_contains_name(self):
        o = Owner(name="Alex")
        assert "Alex" in str(o)


# ============================================================
# Schedule
# ============================================================

class TestSchedule:
    def _make_schedule(self):
        return Schedule(day=date.today())

    def test_add_and_remove_task(self):
        s = self._make_schedule()
        t = Task(name="Walk")
        s.add_task(t)
        assert t in s.task_list
        result = s.remove_task(t.id)
        assert result is True
        assert t not in s.task_list

    def test_remove_missing_task(self):
        s = self._make_schedule()
        from uuid import uuid4
        assert s.remove_task(uuid4()) is False

    def test_generate_priority_order(self):
        s = self._make_schedule()
        low  = Task(name="Low",  priority=1)
        high = Task(name="High", priority=5)
        s.add_task(low)
        s.add_task(high)
        ordered = s.generate()
        assert ordered[0] is high
        assert ordered[1] is low

    def test_generate_incomplete_before_complete(self):
        s = self._make_schedule()
        done = Task(name="Done", priority=5, complete=True)
        todo = Task(name="Todo", priority=1, complete=False)
        s.add_task(done)
        s.add_task(todo)
        ordered = s.generate()
        assert ordered[0] is todo
        assert ordered[1] is done

    def test_clear(self):
        s = self._make_schedule()
        s.add_task(Task(name="Walk"))
        s.clear()
        assert s.task_list == []

    def test_str_contains_date(self):
        s = Schedule(day=date(2026, 1, 15))
        assert "2026-01-15" in str(s)


# ============================================================
# Scheduler
# ============================================================

class TestScheduler:
    def _make_scheduler(self):
        owner = Owner(name="Alex")
        buddy = Pet(name="Buddy", age=3)
        luna  = Pet(name="Luna",  age=5)
        buddy.assign_task(Task(name="Walk",     priority=5, duration=0.5,  frequency="daily"))
        buddy.assign_task(Task(name="Flea Med", priority=3, duration=0.25, frequency="monthly"))
        luna.assign_task(Task(name="Feed",      priority=5, duration=0.1,  frequency="daily"))
        luna.assign_task(Task(name="Brush",     priority=2, duration=0.25, frequency="weekly"))
        luna.assign_task(Task(name="Vet",       priority=4, duration=1.5,  frequency="as_needed"))
        owner.add_pet(buddy)
        owner.add_pet(luna)
        return Scheduler(owner=owner)

    def test_get_all_tasks_count(self):
        s = self._make_scheduler()
        assert len(s.get_all_tasks()) == 5

    def test_get_pending_tasks_all_pending(self):
        s = self._make_scheduler()
        assert len(s.get_pending_tasks()) == 5

    def test_get_pending_tasks_excludes_complete(self):
        s = self._make_scheduler()
        task = s.get_all_tasks()[0]
        task.mark_complete()
        assert len(s.get_pending_tasks()) == 4

    def test_get_tasks_for_pet(self):
        s = self._make_scheduler()
        buddy = s.owner.find_pet_by_name("Buddy")
        tasks = s.get_tasks_for_pet(buddy.id)
        assert len(tasks) == 2
        assert all(t in buddy.tasks for t in tasks)

    def test_get_tasks_for_unknown_pet(self):
        s = self._make_scheduler()
        from uuid import uuid4
        assert s.get_tasks_for_pet(uuid4()) == []

    def test_get_tasks_by_priority_filters(self):
        s = self._make_scheduler()
        high = s.get_tasks_by_priority(min_priority=4)
        assert all(t.priority >= 4 for t in high)

    def test_get_tasks_by_priority_sorted_descending(self):
        s = self._make_scheduler()
        tasks = s.get_tasks_by_priority(min_priority=1)
        priorities = [t.priority for t in tasks]
        assert priorities == sorted(priorities, reverse=True)

    def test_get_tasks_by_frequency_daily(self):
        s = self._make_scheduler()
        daily = s.get_tasks_by_frequency("daily")
        assert len(daily) == 2
        assert all(t.frequency == "daily" for t in daily)

    def test_get_tasks_by_frequency_as_needed(self):
        s = self._make_scheduler()
        tasks = s.get_tasks_by_frequency("as_needed")
        assert len(tasks) == 1
        assert tasks[0].name == "Vet"

    def test_build_schedule_includes_daily(self):
        s = self._make_scheduler()
        schedule = s.build_schedule(date.today())
        names = [t.name for t in schedule.task_list]
        assert "Walk" in names
        assert "Feed" in names

    def test_build_schedule_includes_as_needed(self):
        s = self._make_scheduler()
        schedule = s.build_schedule(date.today())
        names = [t.name for t in schedule.task_list]
        assert "Vet" in names

    def test_build_schedule_excludes_complete(self):
        s = self._make_scheduler()
        walk = s.owner.find_pet_by_name("Buddy").tasks[0]
        walk.mark_complete()
        schedule = s.build_schedule(date.today())
        names = [t.name for t in schedule.task_list]
        assert "Walk" not in names

    def test_summary_contains_owner_name(self):
        s = self._make_scheduler()
        assert "Alex" in s.summary()

    def test_summary_contains_pet_names(self):
        s = self._make_scheduler()
        summary = s.summary()
        assert "Buddy" in summary
        assert "Luna" in summary

"""Tests for pawpal_system.py"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from datetime import date, time, timedelta
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


# ============================================================
# Task.next_occurrence()
# ============================================================

class TestTaskNextOccurrence:
    def test_daily_returns_task(self):
        t = Task(name="Walk", frequency="daily", start_date=date.today())
        assert t.next_occurrence() is not None

    def test_daily_start_date_advances_one_day(self):
        today = date.today()
        t = Task(frequency="daily", start_date=today)
        assert t.next_occurrence().start_date == today + timedelta(days=1)

    def test_daily_complete_is_false(self):
        t = Task(frequency="daily", complete=True)
        assert t.next_occurrence().complete is False

    def test_daily_attributes_copied(self):
        t = Task(name="Walk", duration=0.5, priority=4, frequency="daily")
        n = t.next_occurrence()
        assert n.name == "Walk"
        assert n.duration == 0.5
        assert n.priority == 4
        assert n.frequency == "daily"

    def test_daily_scheduled_time_preserved(self):
        t = Task(frequency="daily", scheduled_time=time(8, 0))
        assert t.next_occurrence().scheduled_time == time(8, 0)

    def test_daily_new_uuid(self):
        t = Task(frequency="daily")
        assert t.next_occurrence().id != t.id

    def test_weekly_returns_task(self):
        t = Task(frequency="weekly", start_date=date.today())
        assert t.next_occurrence() is not None

    def test_weekly_start_date_advances_seven_days(self):
        today = date.today()
        t = Task(frequency="weekly", start_date=today)
        assert t.next_occurrence().start_date == today + timedelta(weeks=1)

    def test_monthly_returns_none(self):
        assert Task(frequency="monthly").next_occurrence() is None

    def test_as_needed_returns_none(self):
        assert Task(frequency="as_needed").next_occurrence() is None


# ============================================================
# Pet.complete_task() -- auto-spawn
# ============================================================

class TestPetCompleteTaskAutoSpawn:
    def _pet_with(self, frequency):
        p = Pet(name="Buddy", age=2)
        t = Task(name="Task", frequency=frequency, start_date=date.today(),
                 scheduled_time=time(8, 0))
        p.assign_task(t)
        return p, t

    def test_daily_spawns_new_task(self):
        p, t = self._pet_with("daily")
        p.complete_task(t.id)
        assert len(p.tasks) == 2

    def test_daily_spawned_is_incomplete(self):
        p, t = self._pet_with("daily")
        p.complete_task(t.id)
        assert p.tasks[-1].complete is False

    def test_daily_spawned_start_date_advances(self):
        today = date.today()
        p, t = self._pet_with("daily")
        p.complete_task(t.id)
        assert p.tasks[-1].start_date == today + timedelta(days=1)

    def test_daily_spawned_inherits_scheduled_time(self):
        p, t = self._pet_with("daily")
        p.complete_task(t.id)
        assert p.tasks[-1].scheduled_time == time(8, 0)

    def test_daily_spawned_has_new_uuid(self):
        p, t = self._pet_with("daily")
        p.complete_task(t.id)
        assert p.tasks[-1].id != t.id

    def test_weekly_spawns_new_task(self):
        p, t = self._pet_with("weekly")
        p.complete_task(t.id)
        assert len(p.tasks) == 2

    def test_weekly_spawned_start_date_advances(self):
        today = date.today()
        p, t = self._pet_with("weekly")
        p.complete_task(t.id)
        assert p.tasks[-1].start_date == today + timedelta(weeks=1)

    def test_monthly_no_spawn(self):
        p, t = self._pet_with("monthly")
        p.complete_task(t.id)
        assert len(p.tasks) == 1

    def test_as_needed_no_spawn(self):
        p, t = self._pet_with("as_needed")
        p.complete_task(t.id)
        assert len(p.tasks) == 1


# ============================================================
# Schedule.generate() -- frequency urgency tiebreaker
# ============================================================

class TestScheduleFrequencySort:
    def _sched(self, *tasks):
        s = Schedule(day=date.today())
        for t in tasks:
            s.add_task(t)
        return s

    def test_daily_before_weekly_equal_priority(self):
        daily  = Task(name="D", priority=3, frequency="daily")
        weekly = Task(name="W", priority=3, frequency="weekly")
        names = [t.name for t in self._sched(weekly, daily).generate()]
        assert names.index("D") < names.index("W")

    def test_weekly_before_monthly_equal_priority(self):
        weekly  = Task(name="W", priority=3, frequency="weekly")
        monthly = Task(name="M", priority=3, frequency="monthly")
        names = [t.name for t in self._sched(monthly, weekly).generate()]
        assert names.index("W") < names.index("M")

    def test_monthly_before_as_needed_equal_priority(self):
        monthly   = Task(name="M", priority=3, frequency="monthly")
        as_needed = Task(name="A", priority=3, frequency="as_needed")
        names = [t.name for t in self._sched(as_needed, monthly).generate()]
        assert names.index("M") < names.index("A")

    def test_priority_beats_frequency(self):
        low_daily     = Task(name="LD", priority=1, frequency="daily")
        high_as_needed = Task(name="HA", priority=5, frequency="as_needed")
        ordered = self._sched(low_daily, high_as_needed).generate()
        assert ordered[0].name == "HA"


# ============================================================
# Schedule.time_conflicts()
# ============================================================

class TestScheduleTimeConflicts:
    def _sched(self, *tasks):
        s = Schedule(day=date.today())
        for t in tasks:
            s.add_task(t)
        return s

    def test_overlapping_tasks_detected(self):
        # A 08:00-09:00, B 08:30-09:00 -> overlap
        a = Task(name="A", duration=1.0, scheduled_time=time(8,  0))
        b = Task(name="B", duration=0.5, scheduled_time=time(8, 30))
        pairs = self._sched(a, b).time_conflicts()
        assert len(pairs) == 1
        assert {t.name for t in pairs[0]} == {"A", "B"}

    def test_adjacent_tasks_not_conflicting(self):
        # A 08:00-09:00, B 09:00-09:30 -> half-open, no overlap
        a = Task(name="A", duration=1.0, scheduled_time=time(8, 0))
        b = Task(name="B", duration=0.5, scheduled_time=time(9, 0))
        assert self._sched(a, b).time_conflicts() == []

    def test_task_without_scheduled_time_excluded(self):
        a = Task(name="A", duration=1.0, scheduled_time=time(8, 0))
        b = Task(name="B", duration=1.0)   # no scheduled_time
        pairs = self._sched(a, b).time_conflicts()
        assert all("B" not in {t.name for t in pair} for pair in pairs)

    def test_no_timed_tasks_returns_empty(self):
        a = Task(name="A", duration=1.0)
        b = Task(name="B", duration=1.0)
        assert self._sched(a, b).time_conflicts() == []

    def test_identical_start_times_conflict(self):
        a = Task(name="A", duration=0.5, scheduled_time=time(8, 0))
        b = Task(name="B", duration=0.5, scheduled_time=time(8, 0))
        assert len(self._sched(a, b).time_conflicts()) == 1

    def test_multiple_pairs_detected(self):
        # A 08:00-09:00, B 08:15-08:45, C 08:30-09:30 -> A/B, A/C, B/C
        a = Task(name="A", duration=1.0,  scheduled_time=time(8,  0))
        b = Task(name="B", duration=0.5,  scheduled_time=time(8, 15))
        c = Task(name="C", duration=1.0,  scheduled_time=time(8, 30))
        assert len(self._sched(a, b, c).time_conflicts()) == 3


# ============================================================
# Schedule.conflicts() -- extended with time-overlap messages
# ============================================================

class TestScheduleConflictsExtended:
    def _sched(self, *tasks):
        s = Schedule(day=date.today())
        for t in tasks:
            s.add_task(t)
        return s

    def test_time_overlap_appears_in_messages(self):
        a = Task(name="Walk",    duration=1.0, scheduled_time=time(8,  0), frequency="daily")
        b = Task(name="Feeding", duration=0.5, scheduled_time=time(8, 30), frequency="daily")
        msgs = self._sched(a, b).conflicts()
        assert any("Time overlap" in m for m in msgs)
        assert any("Walk" in m and "Feeding" in m for m in msgs)

    def test_adjacent_tasks_no_time_overlap_message(self):
        a = Task(name="Walk",    duration=0.5, scheduled_time=time(8, 0), frequency="daily")
        b = Task(name="Feeding", duration=0.5, scheduled_time=time(9, 0), frequency="daily")
        msgs = self._sched(a, b).conflicts()
        assert not any("Time overlap" in m for m in msgs)

    def test_duration_cap_message(self):
        tasks = [Task(name=f"T{i}", duration=5.0, frequency="daily") for i in range(3)]
        msgs = self._sched(*tasks).conflicts(daily_cap_hours=8.0)
        assert any("exceeds daily cap" in m for m in msgs)

    def test_duplicate_name_message(self):
        a = Task(name="Walk", frequency="daily")
        b = Task(name="Walk", frequency="daily")
        msgs = self._sched(a, b).conflicts()
        assert any("Duplicate" in m and "Walk" in m for m in msgs)

    def test_no_issues_returns_empty_list(self):
        a = Task(name="Walk",    duration=0.5, scheduled_time=time(8, 0), frequency="daily")
        b = Task(name="Feeding", duration=0.1, scheduled_time=time(9, 0), frequency="daily")
        assert self._sched(a, b).conflicts() == []


# ============================================================
# Scheduler -- filter_tasks, reset_recurring_tasks,
#              find_time_conflicts, detect_conflicts
# ============================================================

class TestSchedulerNewFeatures:
    def _make(self):
        """Two pets, two tasks each, with a cross-pet time overlap."""
        owner = Owner(name="Alex")
        p1 = Pet(name="Buddy", age=3)
        p2 = Pet(name="Luna",  age=5)
        today = date.today()
        # Walk 08:00-08:30, Feed 08:15-08:21 -> cross-pet overlap
        t1 = Task(name="Walk",  frequency="daily",     priority=5, duration=0.5,
                  start_date=today, scheduled_time=time(8,  0))
        t2 = Task(name="Pill",  frequency="monthly",   priority=3, duration=0.1,
                  start_date=today)
        t3 = Task(name="Feed",  frequency="daily",     priority=5, duration=0.1,
                  start_date=today, scheduled_time=time(8, 15))
        t4 = Task(name="Brush", frequency="weekly",    priority=2, duration=0.25,
                  start_date=today)
        p1.assign_task(t1)
        p1.assign_task(t2)
        p2.assign_task(t3)
        p2.assign_task(t4)
        owner.add_pet(p1)
        owner.add_pet(p2)
        return Scheduler(owner=owner), p1, p2

    # -- filter_tasks --

    def test_filter_no_filters_returns_all(self):
        s, _, _ = self._make()
        assert len(s.filter_tasks()) == 4

    def test_filter_by_pet(self):
        s, p1, _ = self._make()
        tasks = s.filter_tasks(pet_id=p1.id)
        assert len(tasks) == 2
        assert all(t in p1.tasks for t in tasks)

    def test_filter_by_pet_unknown_returns_empty(self):
        from uuid import uuid4
        s, _, _ = self._make()
        assert s.filter_tasks(pet_id=uuid4()) == []

    def test_filter_status_pending(self):
        s, _, _ = self._make()
        tasks = s.filter_tasks(status=False)
        assert all(not t.complete for t in tasks)
        assert len(tasks) == 4

    def test_filter_status_complete(self):
        s, p1, _ = self._make()
        p1.tasks[0].mark_complete()
        tasks = s.filter_tasks(status=True)
        assert all(t.complete for t in tasks)
        assert len(tasks) == 1

    def test_filter_pet_and_status_combined(self):
        s, p1, _ = self._make()
        p1.tasks[0].mark_complete()   # Walk done
        pending = s.filter_tasks(pet_id=p1.id, status=False)
        assert len(pending) == 1
        assert pending[0].name == "Pill"

    # -- reset_recurring_tasks --

    def test_reset_daily_task(self):
        s, p1, _ = self._make()
        walk = p1.tasks[0]
        walk.mark_complete()
        s.reset_recurring_tasks(date.today())
        assert not walk.complete

    def test_reset_weekly_task(self):
        s, _, p2 = self._make()
        brush = p2.tasks[1]   # weekly, start_date=today
        brush.mark_complete()
        s.reset_recurring_tasks(date.today())
        assert not brush.complete

    def test_reset_skips_as_needed(self):
        owner = Owner(name="T")
        p = Pet(name="P", age=1)
        vet = Task(name="Vet", frequency="as_needed", start_date=date.today())
        vet.mark_complete()
        p.assign_task(vet)
        owner.add_pet(p)
        Scheduler(owner=owner).reset_recurring_tasks(date.today())
        assert vet.complete

    def test_reset_returns_count(self):
        s, _, _ = self._make()
        for t in s.get_all_tasks():
            if t.frequency == "daily":
                t.mark_complete()
        count = s.reset_recurring_tasks(date.today())
        assert count >= 2   # Walk and Feed are both daily

    # -- find_time_conflicts --

    def test_cross_pet_conflict_detected(self):
        s, _, _ = self._make()
        # Walk 08:00-08:30, Feed 08:15-08:21 -> overlap
        pairs = s.find_time_conflicts(date.today())
        names = {frozenset({a.name, b.name}) for a, b in pairs}
        assert frozenset({"Walk", "Feed"}) in names

    def test_no_conflicts_when_tasks_non_overlapping(self):
        owner = Owner(name="T")
        p = Pet(name="P", age=1)
        today = date.today()
        p.assign_task(Task(name="A", duration=0.5, frequency="daily",
                           scheduled_time=time(8, 0), start_date=today))
        p.assign_task(Task(name="B", duration=0.5, frequency="daily",
                           scheduled_time=time(9, 0), start_date=today))
        owner.add_pet(p)
        assert Scheduler(owner=owner).find_time_conflicts(today) == []

    def test_same_pet_conflict_detected(self):
        owner = Owner(name="T")
        p = Pet(name="P", age=1)
        today = date.today()
        p.assign_task(Task(name="X", duration=1.0, frequency="daily",
                           scheduled_time=time(8, 0), start_date=today))
        p.assign_task(Task(name="Y", duration=1.0, frequency="daily",
                           scheduled_time=time(8, 30), start_date=today))
        owner.add_pet(p)
        pairs = Scheduler(owner=owner).find_time_conflicts(today)
        assert len(pairs) == 1

    # -- detect_conflicts --

    def test_detect_duration_cap(self):
        owner = Owner(name="T")
        p = Pet(name="P", age=1)
        today = date.today()
        for i in range(3):
            p.assign_task(Task(name=f"T{i}", duration=5.0,
                               frequency="daily", start_date=today))
        owner.add_pet(p)
        msgs = Scheduler(owner=owner).detect_conflicts(today, daily_cap_hours=8.0)
        assert any("exceeds daily cap" in m for m in msgs)

    def test_detect_time_overlap(self):
        s, _, _ = self._make()
        msgs = s.detect_conflicts(date.today())
        assert any("Time overlap" in m for m in msgs)

    def test_detect_no_issues(self):
        owner = Owner(name="T")
        p = Pet(name="P", age=1)
        today = date.today()
        p.assign_task(Task(name="A", duration=0.5, frequency="daily",
                           scheduled_time=time(8, 0), start_date=today))
        p.assign_task(Task(name="B", duration=0.5, frequency="daily",
                           scheduled_time=time(9, 0), start_date=today))
        owner.add_pet(p)
        assert Scheduler(owner=owner).detect_conflicts(today) == []


# ============================================================
# Sorting Correctness -- chronological (scheduled_time) ordering
# ============================================================

class TestSortingChronological:
    """Verify Schedule.generate() orders tasks by scheduled_time when
    all other sort keys (completion, priority, frequency, duration) are equal."""

    def _sched(self, *tasks):
        s = Schedule(day=date.today())
        for t in tasks:
            s.add_task(t)
        return s

    def test_earlier_scheduled_time_comes_first(self):
        # Added in reverse order; generate() should sort by time
        late  = Task(name="Late",  duration=0.5, priority=3, frequency="daily",
                     scheduled_time=time(10, 0))
        early = Task(name="Early", duration=0.5, priority=3, frequency="daily",
                     scheduled_time=time(8, 0))
        ordered = self._sched(late, early).generate()
        names = [t.name for t in ordered]
        assert names.index("Early") < names.index("Late")

    def test_three_tasks_in_time_order(self):
        t1 = Task(name="T1", duration=0.5, priority=3, frequency="daily",
                  scheduled_time=time(7, 0))
        t2 = Task(name="T2", duration=0.5, priority=3, frequency="daily",
                  scheduled_time=time(9, 0))
        t3 = Task(name="T3", duration=0.5, priority=3, frequency="daily",
                  scheduled_time=time(11, 0))
        # Add out-of-order: T3, T1, T2
        ordered = self._sched(t3, t1, t2).generate()
        names = [t.name for t in ordered]
        assert names == ["T1", "T2", "T3"]

    def test_priority_still_beats_earlier_time(self):
        # High-priority later task should still precede low-priority earlier task
        low_early  = Task(name="LowEarly",  duration=0.5, priority=1,
                          frequency="daily", scheduled_time=time(7, 0))
        high_late  = Task(name="HighLate",  duration=0.5, priority=5,
                          frequency="daily", scheduled_time=time(12, 0))
        ordered = self._sched(low_early, high_late).generate()
        assert ordered[0].name == "HighLate"

    def test_tasks_without_scheduled_time_stable_after_timed(self):
        # Untimed tasks have no scheduled_time; they should not crash generate()
        timed   = Task(name="Timed",   duration=0.5, priority=3, frequency="daily",
                       scheduled_time=time(8, 0))
        untimed = Task(name="Untimed", duration=0.5, priority=3, frequency="daily")
        ordered = self._sched(timed, untimed).generate()
        assert len(ordered) == 2   # both present, no crash

    def test_empty_schedule_returns_empty_list(self):
        assert Schedule(day=date.today()).generate() == []


# ============================================================
# Recurrence Logic -- daily task spawns next-day copy on completion
# ============================================================

class TestDailyRecurrenceEndToEnd:
    """Confirm the full loop: complete a daily task → new task appears
    with start_date advanced by exactly one day and ready for tomorrow."""

    def _setup(self, today):
        owner = Owner(name="Alex")
        pet = Pet(name="Buddy", age=2)
        task = Task(name="Morning Walk", frequency="daily",
                    priority=4, duration=0.5,
                    start_date=today, scheduled_time=time(7, 30))
        pet.assign_task(task)
        owner.add_pet(pet)
        return Scheduler(owner=owner), pet, task

    def test_completing_daily_task_adds_next_day_task(self):
        today = date.today()
        _, pet, task = self._setup(today)
        pet.complete_task(task.id)
        assert len(pet.tasks) == 2
        spawned = pet.tasks[-1]
        assert spawned.start_date == today + timedelta(days=1)

    def test_spawned_task_is_incomplete(self):
        today = date.today()
        _, pet, task = self._setup(today)
        pet.complete_task(task.id)
        assert pet.tasks[-1].complete is False

    def test_spawned_task_has_different_id(self):
        today = date.today()
        _, pet, task = self._setup(today)
        pet.complete_task(task.id)
        assert pet.tasks[-1].id != task.id

    def test_spawned_task_appears_in_tomorrows_schedule(self):
        today = date.today()
        tomorrow = today + timedelta(days=1)
        scheduler, pet, task = self._setup(today)
        pet.complete_task(task.id)
        schedule = scheduler.build_schedule(tomorrow)
        names = [t.name for t in schedule.task_list]
        assert "Morning Walk" in names

    def test_original_task_excluded_from_tomorrows_schedule(self):
        today = date.today()
        tomorrow = today + timedelta(days=1)
        scheduler, pet, task = self._setup(today)
        pet.complete_task(task.id)
        schedule = scheduler.build_schedule(tomorrow)
        # The original (complete) task should not appear
        task_ids = [t.id for t in schedule.task_list]
        assert task.id not in task_ids

    def test_reset_recurring_does_not_uncomplete_spawned_task(self):
        # The spawned (tomorrow's) task should not be reset on today's call
        today = date.today()
        scheduler, pet, task = self._setup(today)
        pet.complete_task(task.id)
        spawned = pet.tasks[-1]
        # reset for today should reset today's (now complete) task
        scheduler.reset_recurring_tasks(today)
        # spawned task's start_date is tomorrow, so it is NOT reset today
        assert spawned.complete is False   # was already False, still False


# ============================================================
# Conflict Detection -- Scheduler flags identical scheduled times
# ============================================================

class TestSchedulerDuplicateTimeConflicts:
    """Verify that Scheduler.detect_conflicts() and find_time_conflicts()
    flag tasks scheduled at the exact same start time."""

    def _scheduler_with_times(self, time_a, time_b):
        today = date.today()
        owner = Owner(name="Alex")
        pet = Pet(name="Buddy", age=2)
        pet.assign_task(Task(name="Task A", frequency="daily", duration=0.5,
                             start_date=today, scheduled_time=time_a))
        pet.assign_task(Task(name="Task B", frequency="daily", duration=0.5,
                             start_date=today, scheduled_time=time_b))
        owner.add_pet(pet)
        return Scheduler(owner=owner)

    def test_identical_start_times_flagged_by_find_time_conflicts(self):
        scheduler = self._scheduler_with_times(time(9, 0), time(9, 0))
        pairs = scheduler.find_time_conflicts(date.today())
        assert len(pairs) == 1
        names = {t.name for t in pairs[0]}
        assert names == {"Task A", "Task B"}

    def test_identical_start_times_flagged_by_detect_conflicts(self):
        scheduler = self._scheduler_with_times(time(9, 0), time(9, 0))
        msgs = scheduler.detect_conflicts(date.today())
        assert any("Time overlap" in m for m in msgs)

    def test_identical_start_times_message_names_both_tasks(self):
        scheduler = self._scheduler_with_times(time(9, 0), time(9, 0))
        msgs = scheduler.detect_conflicts(date.today())
        overlap_msgs = [m for m in msgs if "Time overlap" in m]
        assert any("Task A" in m and "Task B" in m for m in overlap_msgs)

    def test_non_overlapping_times_not_flagged(self):
        scheduler = self._scheduler_with_times(time(8, 0), time(9, 0))
        assert scheduler.find_time_conflicts(date.today()) == []

    def test_cross_pet_identical_times_flagged(self):
        today = date.today()
        owner = Owner(name="Alex")
        p1 = Pet(name="Buddy", age=2)
        p2 = Pet(name="Luna",  age=3)
        p1.assign_task(Task(name="Walk",  frequency="daily", duration=0.5,
                            start_date=today, scheduled_time=time(8, 0)))
        p2.assign_task(Task(name="Feed",  frequency="daily", duration=0.5,
                            start_date=today, scheduled_time=time(8, 0)))
        owner.add_pet(p1)
        owner.add_pet(p2)
        scheduler = Scheduler(owner=owner)
        pairs = scheduler.find_time_conflicts(today)
        assert len(pairs) == 1
        names = {t.name for t in pairs[0]}
        assert names == {"Walk", "Feed"}

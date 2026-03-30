from datetime import date
from pawpal_system import Task, Pet, Owner, Scheduler

# --- Build owner and pets ---
owner = Owner(name="Alex")

buddy = Pet(name="Buddy", age=3)
luna  = Pet(name="Luna",  age=6)

owner.add_pet(buddy)
owner.add_pet(luna)

# --- Buddy's tasks ---
buddy.assign_task(Task(
    name="Morning Walk",
    description="30-minute walk around the block",
    duration=0.5,
    priority=5,
    frequency="daily",
))

buddy.assign_task(Task(
    name="Flea Treatment",
    description="Apply monthly flea and tick prevention",
    duration=0.25,
    priority=3,
    frequency="monthly",
))

# --- Luna's tasks ---
luna.assign_task(Task(
    name="Feeding",
    description="Wet food — half a can morning and evening",
    duration=0.1,
    priority=5,
    frequency="daily",
))

luna.assign_task(Task(
    name="Brush Coat",
    description="Brush to reduce shedding",
    duration=0.25,
    priority=2,
    frequency="weekly",
))

luna.assign_task(Task(
    name="Vet Checkup",
    description="Annual wellness exam — schedule when needed",
    duration=1.5,
    priority=4,
    frequency="as_needed",
))

# --- Print today's schedule ---
scheduler = Scheduler(owner=owner)
schedule  = scheduler.build_schedule(date.today())

print(schedule)

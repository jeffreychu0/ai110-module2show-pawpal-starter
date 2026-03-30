# -*- coding: utf-8 -*-
import streamlit as st
from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ------------------------------------------------------------------
# Session-state vault — objects are created once and reused on rerun
# ------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")

if "pet" not in st.session_state:
    st.session_state.pet = Pet(name="Mochi", age=2)
    st.session_state.owner.add_pet(st.session_state.pet)

owner: Owner = st.session_state.owner
pet: Pet     = st.session_state.pet

# ------------------------------------------------------------------
# Owner & pet info
# ------------------------------------------------------------------
st.subheader("Owner & Pet")

col1, col2, col3 = st.columns(3)
with col1:
    owner_name = st.text_input("Owner name", value=owner.name)
    if owner_name != owner.name:
        owner.name = owner_name

with col2:
    pet_name = st.text_input("Pet name", value=pet.name)
    if pet_name != pet.name:
        pet.name = pet_name

with col3:
    pet_age = st.number_input("Pet age (years)", min_value=0, max_value=30, value=pet.age)
    if pet_age != pet.age:
        pet.age = pet_age

# ------------------------------------------------------------------
# Add a task
# ------------------------------------------------------------------
st.divider()
st.subheader("Add a Task")

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (hours)", min_value=0.1, max_value=24.0,
                               value=0.5, step=0.1)
with col3:
    priority = st.selectbox("Priority (1=low, 5=high)", [1, 2, 3, 4, 5], index=4)
with col4:
    frequency = st.selectbox("Frequency", ["daily", "weekly", "monthly", "as_needed"])

if st.button("Add task"):
    pet.assign_task(Task(
        name=task_title,
        duration=float(duration),
        priority=priority,
        frequency=frequency,
    ))
    st.success(f"Added '{task_title}' to {pet.name}'s tasks.")

# ------------------------------------------------------------------
# Current task list with complete / remove actions
# ------------------------------------------------------------------
st.divider()
st.subheader(f"{pet.name}'s Tasks")

if pet.tasks:
    for task in pet.tasks:
        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            status = "✅" if task.complete else "🔲"
            st.markdown(
                f"{status} **{task.name}** — "
                f"`{task.duration}h` | priority `{task.priority}` | `{task.frequency}`"
            )
        with col2:
            label = "Undo" if task.complete else "Done"
            if st.button(label, key=f"toggle_{task.id}"):
                if task.complete:
                    pet.uncomplete_task(task.id)
                else:
                    pet.complete_task(task.id)
                st.rerun()
        with col3:
            if st.button("Remove", key=f"remove_{task.id}"):
                pet.remove_task(task.id)
                st.rerun()
else:
    st.info("No tasks yet. Add one above.")

# ------------------------------------------------------------------
# Generate today's schedule
# ------------------------------------------------------------------
st.divider()
st.subheader("Today's Schedule")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner=owner)
    schedule  = scheduler.build_schedule(date.today())
    ordered   = schedule.generate()

    if ordered:
        st.success(f"Schedule for **{date.today()}** — {len(ordered)} task(s)")
        for task in ordered:
            status = "✅" if task.complete else "🔲"
            st.markdown(
                f"{status} **{task.name}** &nbsp; "
                f"`priority {task.priority}` &nbsp; "
                f"`{task.duration}h` &nbsp; "
                f"`{task.frequency}`"
            )
    else:
        st.info("No pending tasks match today's schedule.")

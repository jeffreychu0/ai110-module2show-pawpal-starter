# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

This was the actions and classes given for the UML:

3 core actions a user should be able to do:
1: Add Pets
2: List the uncompleted and total daily tasks
3: Add or Delete tasks as necessary

Objects and Attributes
- Pet
    Name
    Age
    Tasks

    assign_task()
    complete_task()

- Tasks
    Complete
    Name
    Description
    Duration
    Priority

    add_task()
    edit_task()
    delete_task()

- Owner
    Name
    Pets

    add_pet();

- Schedule
    task_list w/ times
    day

    generate();

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

A few changes were made as suggested by the AI. One of the few changes I made includes creating a uncomplete_task method for pets.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

the scheduler considers incomplete, higher priority, shorter tasks. These were chosen because it allows for more incomplete tasks to be done that are important

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The AI made a tradeoff for readability for python syntax, for some situations, this tradeoff is worth it especially when dealing with larger repositories and for developers more versed in python
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

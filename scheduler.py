import datetime
import threading
import time

# Define a function to execute a task
def execute_task(task_name):
    print(f"Task '{task_name}' executed at {datetime.datetime.now()}")

# Scheduler function that waits for a specific time and then runs a task
def schedule_task(task_name, target_time):
    while True:
        now = datetime.datetime.now()
        if now >= target_time:
            execute_task(task_name)
            break
        time.sleep(1)  # Wait 1 second before checking again

# Define tasks with their target times
tasks = [
    {"name": "Task 1", "time": datetime.datetime.now() + datetime.timedelta(seconds=5)},
    {"name": "Task 2", "time": datetime.datetime.now() + datetime.timedelta(seconds=10)},
]

# Use threading to schedule multiple tasks
threads = []
for task in tasks:
    t = threading.Thread(target=schedule_task, args=(task["name"], task["time"]))
    threads.append(t)
    t.start()

# Wait for all tasks to finish
for t in threads:
    t.join()

print("All tasks completed.")
# Simple script that uses the Todoist API to manage "optional" tagged tasks.
# Tasks that are optional are tagged with the label "optional".
# The script moves optional tasks that are overdue to the next week.

from datetime import datetime, timedelta
import time
import os
from todoist_api_python.api import TodoistAPI

class TodoistRescheduler:
    def __init__(self, api_token):
        self._api = TodoistAPI(api_token)

    def _IsTaskOverdue(self, due_date):
        """Check if a task is overdue."""
        return datetime.strptime(due_date, '%Y-%m-%d') < datetime.now()

    def _RescheduleTask(self, task_id, new_due_date):
        """Reschedule a task to a new due date."""
        self._api.update_task(task_id=task_id, due_date=new_due_date.strftime('%Y-%m-%d'))
        print(f"Rescheduled task {task_id} to {new_due_date}")

    def CheckAndRescheduleTasks(self):
        """Check and reschedule overdue tasks marked as optional."""
        try:
            tasks = self._api.get_tasks()
            for task in tasks:
                if 'optional' in task.labels and task.due and not task.is_completed:
                    if self._IsTaskOverdue(task.due.date):
                        new_due_date = datetime.now() + timedelta(weeks=1) # Reschedule to next week
                        self._RescheduleTask(task.id, new_due_date)

        except Exception as error:
            # If error contains "Unauthorized", the API key is invalid
            isInvalidApiKey = 'Unauthorized' in str(error)

            if(isInvalidApiKey):
                print("!! Invalid API key. Ensure the env variable TODOIST_API_KEY is set correctly.")

            print("Err: " + error)

if __name__ == '__main__':
    apikey = os.getenv('TODOIST_API_KEY')
    rescheduler = TodoistRescheduler(apikey)

    print("Starting rescheduler...")
    while True:
        print("Checking for overdue tasks...")
        rescheduler.CheckAndRescheduleTasks()
        time.sleep(600)  # Wait for 10 minutes before next check

    print("Rescheduler stopped.")

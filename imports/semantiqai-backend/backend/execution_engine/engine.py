from .storage import get_user, update_user
from .planner import generate_plan
from .tasks import add_task, complete_task
from .habits import add_habit, complete_habit
from .workflow import create_workflow
from .automation import run_automation

def create_goal_plan(goal):
    return generate_plan(goal)

def add_user_task(user_id, task):
    user = get_user(user_id)
    user = add_task(user, task)
    update_user(user_id, user)
    return user

def finish_task(user_id, index):
    user = get_user(user_id)
    user = complete_task(user, index)
    update_user(user_id, user)
    return user

def add_user_habit(user_id, habit):
    user = get_user(user_id)
    user = add_habit(user, habit)
    update_user(user_id, user)
    return user

def finish_habit(user_id, index):
    user = get_user(user_id)
    user = complete_habit(user, index)
    update_user(user_id, user)
    return user

def create_user_workflow(name, steps):
    return create_workflow(name, steps)

def execute_workflow(workflow):
    return run_automation(workflow)

import uuid

from .models import Task
from .models import db

def submit_task(data:dict) -> str:
    if data.get('taskDescription'):
        data['taskDescription'] = ""
        
    if data.get('branch'):
        data['branch'] = ""
    
    if data.get('commitId'):
        data['commitId'] = ""
        
    data['task_id'] = uuid.uuid4()
    task = Task(task_id=data['task_id'],
        taskName=data['taskName'], taskDescription=data['taskDescription'], 
                timestamp=data['timestamp'], repo=data['repo'], branch=data['branch'], 
                commitId=data['commitId'], operate=data['operate'])
    db.session.add(task)
    db.session.commit()
    return data['task_id']
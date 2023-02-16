from .models import db,taskRun
import datetime

def run_task(data):
    task_id = data['taksId']
    runner = data['windows-robot1']
    time_now = datetime.datetime.utcnow()
    
    new_run_task = run_task(
        task_id = task_id,
        runner = runner,
        timestamp = time_now,
    )
    db.session.add(runner)
    db.session.commit()
    
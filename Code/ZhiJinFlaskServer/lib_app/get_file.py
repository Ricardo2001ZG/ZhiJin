from .models import File


def get_file(task_id=str|None, md5=str|None) -> list:
    if task_id:
        files = File.query.filter_by(task_id=task_id).all()
    elif md5:
        files = File.query.filter_by(md5=md5).all()
    else:
        files = File.query.all()

    result = []
    for file in files:
        result.append({
            "file_name": file.file_name,
            "file_size": file.file_size,
            "file_path": file.file_path,
            "md5": file.md5,
            "timestamp": file.timestamp,
            "taskId": file.task_id,
        })

    return files


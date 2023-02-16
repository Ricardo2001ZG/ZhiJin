import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

 # 任务列表
class Task(db.Model):
    __tablename__ = 'task'
    task_id = db.Column('task_id', db.String(36), primary_key=True)
    taskName = db.Column(db.String(128), nullable=False)
    taskDescription = db.Column(db.String(4096), default="")
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    repo = db.Column(db.String(2048), nullable=False)
    branch = db.Column(db.String(128), default="master")
    commitId = db.Column(db.String(128), default="")
    operate = db.Column(db.Text, nullable=False)
    status = db.Column(db.Integer, default=1)    # 任务状态

    def __repr__(self) -> str:
        return f"<task_id> {self.task_id}"

# 产物
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Float, nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    md5 = db.Column(db.String(32), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow(), nullable=False)
    task_id = db.Column(db.String(36), db.ForeignKey('task.task_id'), nullable=False)

    def __repr__(self):
        return f'<File {self.file_name}>'
    
# 登记的实例机器
class Instance(db.Model):
    __tablename__ = 'instances'

    id = db.Column(db.Integer, primary_key=True)
    cpu = db.Column(db.Float)
    memory = db.Column(db.Float)
    ip_address = db.Column(db.String(15), unique=True)
    system = db.Column(db.String(128))

    def __init__(self, cpu, memory, ip_address, system):
        self.cpu = cpu
        self.memory = memory
        self.ip_address = ip_address
        self.system = system
        
    def __repr__(self):
        return f'<Instance {self.ip_address}>'
    

## 处理任务
## 这部分交给redis存储比较好
class taskRun(db.Model):
    __tablename__ = 'taskRun'
    task_id = db.Column('task_id', db.String(36), db.ForeignKey('task.task_id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    runner = db.Column(db.String(512),nullable = False)
    
    def __repr__(self):
        return f"<task_id> {self.task_id}"
    
    

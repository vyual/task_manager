import sqlalchemy
from .base import metadata
import datetime

tasks_model = sqlalchemy.Table('tasks',
                               metadata,
                               sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True,
                                                 unique=True),
                               sqlalchemy.Column('name', sqlalchemy.String(255), nullable=False),
                               sqlalchemy.Column('parent_task_id', sqlalchemy.Integer,
                                                 sqlalchemy.ForeignKey('tasks.id'), nullable=True),
                               sqlalchemy.Column('assignee_id', sqlalchemy.Integer,
                                                 sqlalchemy.ForeignKey('users.id'), nullable=True),
                               sqlalchemy.Column('deadline', sqlalchemy.DateTime),
                               sqlalchemy.Column('completed', sqlalchemy.Boolean, default=False),
                               sqlalchemy.Column('created_at', sqlalchemy.DateTime, default=datetime.datetime.utcnow),
                               sqlalchemy.Column('updated_at', sqlalchemy.DateTime, default=datetime.datetime.utcnow))

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .list_title import ListTitle
from .tasks_content import TasksContent
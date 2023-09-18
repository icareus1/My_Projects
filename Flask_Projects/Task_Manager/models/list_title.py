from . import db

class ListTitle(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(255), unique=True, nullable=False)
    tasks = db.relationship('TasksContent', backref='list_title')
    
    def __repr__(self):
        return self.name

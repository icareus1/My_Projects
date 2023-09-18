from . import db

class TasksContent(db.Model): 
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Boolean, default=False, nullable=False)
    title_id = db.Column(db.Integer, db.ForeignKey('list_title.id'), nullable=False)
    
    def __repr__(self):
        return self.name
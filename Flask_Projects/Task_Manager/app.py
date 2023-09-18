from flask import Flask, redirect, request, url_for, render_template
from models import db, ListTitle, TasksContent
from dotenv import load_dotenv
import os
import secrets



load_dotenv()

app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secrets.token_hex(32)

db.init_app(app)


@app.route('/')
def index():
    titles = ListTitle.query.all()
    print(titles)
    return render_template('index.html', titles=titles)


@app.route('/title/<int:title_id>')
def title_content(title_id):
    title = ListTitle.query.get(title_id)
    tasks = TasksContent.query.filter_by(title_id=title_id).all()
    return render_template('task.html', title=title, tasks=tasks)


@app.route('/add_list', methods=['POST'])
def add_list():
    list_title = request.form.get('list_title')
    new_list = ListTitle(name=list_title)
    db.session.add(new_list)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/add_task/<int:title_id>', methods=['POST'])
def add_task(title_id):
    task_name = request.form.get('task_name')
    new_task = TasksContent(name=task_name, title_id=title_id)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('title_content', title_id=title_id))


@app.route('/toggle/<int:task_id>')
def toggle_task(task_id):
    task = TasksContent.query.get(task_id)
    if task:
        task.status = not task.status
        db.session.commit()
    return redirect(url_for('title_content', title_id=task.title_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='localhost', port=8000, debug=True)
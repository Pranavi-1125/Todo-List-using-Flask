# Imorting necessary libraries
from flask import Flask, render_template, redirect, url_for, request    
# from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

#flask class and __name__ is a parameter that helps flask to identify the root path
#This is needed so that Flask knows where to look for resources such as templates and static files.
app = Flask(__name__)

#Adding the file in scss so that scss files are converted to css
# Scss(app)

# Connecting database to the flask app
# URI - Uniform Resource Identifier (Connection string)
# ['SQLALCHEMY_DATABASE_URI'] -> Config key that tells SQLAlchemy where the database is located and how to connect to it.
# sqlite:// → tells SQLAlchemy to use SQLite, a lightweight file-based database.
# database.db → that’s the file name where your database data will live.
# The triple slashes /// mean “the file is in the current project folder”.
# So: this line means “Store my data in a file called database.db right here in my project.”
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # To disable a feature that signals the app every time a change is about to be made in the database. It’s not necessary for this simple app, so we turn it off to save some resources.
db = SQLAlchemy(app)


# ---------------------------Creating a model for the database---------------------------------------------
# Here, we define a class MyTask that inherits from db.Model, which means it represents a table in the database.
# Here id, content, complete, and created are columns in the table in the database.
class MyTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(100), nullable=False)
    complete = db.Column(db.Boolean, default=False)
    created = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self) -> str:
        return f"Task {self.id}"
    
with app.app_context():
    db.create_all()  

# POST - when user submits a form
# GET - when user requests a page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        current_task = request.form['content']        # 'content' is the name attribute of the input field in the HTML form
        new_task = MyTask(content=current_task)     # Creating a new task object
        try: 
            db.session.add(new_task)                 # Adding the new task to the database session
            db.session.commit()                 # Committing the session to save the task in the database
            return redirect("/")                # Redirecting to the index page after successful addition
        except Exception as e:
            print(f"ERROR: {e}")                  # Printing the error message if any exception occurs
            return f"ERROR: {e}"             # Sending the user to the updated index.html page
    else:
        all_tasks = MyTask.query.order_by(MyTask.created).all()  # Querying all tasks from the database, ordered by creation time
        return render_template("index.html", tasks=all_tasks)    # Rendering the index.html template with the list of tasks


# Route to delete a task
@app.route('/delete/<int:id>')
def delete_task(id: int):
    task_to_delete = MyTask.query.get_or_404(id)
    try: 
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect("/")
    except Exception as e:
        print(f"ERROR: {e}")
        return f"ERROR: {e}"
    
# Route to update a task
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_task(id: int):
    task_to_update = MyTask.query.get_or_404(id)
    if request.method == 'POST':
        task_to_update.content = request.form['content']
        # task_to_update.complete = 'complete' in request.form
        try:
            db.session.commit()
            return redirect("/")
        except Exception as e:
            return f"ERROR: {e}"
    else:
        return render_template("edit.html", task=task_to_update)

if __name__ == '__main__':
    app.run(debug=True)
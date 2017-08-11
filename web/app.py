from flask import Flask, render_template, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from flask_socketio import SocketIO
from flask_socketio import join_room, leave_room

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
socketio = SocketIO(app)


class ReusableForm(Form):
    name = TextField('Name:', validators=[validators.required()])
    email = TextField('Email:', validators=[validators.required(), validators.Length(min=6, max=35)])
    password = TextField('Password:', validators=[validators.required(), validators.Length(min=3, max=35)])


@app.route("/", methods=['GET', 'POST'])
def hello():
    form = ReusableForm(request.form)

    print(form.errors)
    if request.method == 'POST':
        name=request.form['name']
        password=request.form['password']
        email=request.form['email']
        print(name, " ", email, " ", password)

        if form.validate():
            # Save the comment here.
            flash('Thanks for registration ' + name)
        else:
            flash('Error: All the form fields are required. ')

    return render_template('hello.html', form=form)


@app.route('/')
@app.route('/index')
def index():
    user = g.user
    posts = [
        {
            'author': { 'nickname': 'John' },
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': { 'nickname': 'Susan' },
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html',
        title = 'Home',
        user = user,
        posts = posts)

@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)

@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))


if __name__ == "__main__":
    socketio.run(app)
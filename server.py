from flask import Flask, render_template, redirect, request, session, flash
import re, md5
from mysqlconnection import MySQLConnector
app = Flask(__name__)
app.secret_key = "DINGUS"
mysql = MySQLConnector(app, 'wall')

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d$@$!%*?&]{8,}')

@app.route('/')
def index():
    session['previous_email'] = ""
    session['previous_first_name'] = ""
    session['previous_last_name'] = ""
    if 'logged_in' not in session:
        session['logged_in'] = False
    if session['logged_in']:
        print "User ID: " + str(session['logged_in']['id'])
        dbusers = mysql.query_db("SELECT * FROM users")
        dbmessages = mysql.query_db("SELECT * FROM messages")
        dbcomments = mysql.query_db("SELECT * FROM comments")
        tmessages = []
        for dbmessage in dbmessages:
            print "Message Author ID: " + str(dbmessage['user_id'])
            print str(dbmessage['user_id'] == session['logged_in']['id'])
            tmessage = {}
            for dbuser in dbusers:
                if dbuser['id'] == dbmessage['user_id']:
                    tmessage['user'] = dbuser['first_name'] + " " + dbuser['last_name']
            if dbmessage['updated_at'] > dbmessage['created_at']:
                tmessage['timestamp'] = dbmessage['updated_at']
            else:
                tmessage['timestamp'] = dbmessage['created_at']
            tmessage['message'] = dbmessage['message']
            tmessage['id'] = dbmessage['user_id']
            if dbmessage['user_id'] == session['logged_in']['id']:
                tmessage['deleteable'] = True
            else:
                tmessage['deleteable'] = False
            tmessage['comments'] = []
            for dbcomment in dbcomments:
                if dbcomment['message_id'] == dbmessage['id']:
                    print "Comment Author ID: " + str(dbcomment['user_id'])
                    tcomment = {}
                    for cdbuser in dbusers:
                        if cdbuser['id'] == dbcomment['user_id']:
                            tcomment['user'] = cdbuser['first_name'] + " " + cdbuser['last_name']
                    if dbcomment['updated_at'] > dbcomment['created_at']:
                        tcomment['timestamp'] = dbcomment['updated_at']
                    else:
                        tcomment['timestamp'] = dbcomment['created_at']
                    tcomment['comment'] = dbcomment['comment']
                    tcomment['id'] = dbcomment['user_id']
                    if dbcomment['user_id'] == session['logged_in']['id']:
                        tcomment['deleteable'] = True
                    else:
                        tcomment['deleteable'] = False
                    tmessage['comments'].append(tcomment)
            tmessages.append(tmessage)
        return render_template("index.html", users=mysql.query_db("SELECT * FROM users"), logged_in=True, email=session['logged_in']['email'], messages=tmessages)
    return render_template("index.html", users=mysql.query_db("SELECT * FROM users"))

@app.route('/register')
def register():
    if 'previous_email' not in session or 'previous_first_name' not in session or 'previous_last_name' not in session:
        session['previous_email'] = ""
        session['previous_first_name'] = ""
        session['previous_last_name'] = ""
    return render_template("register.html", previous_email= session['previous_email'], previous_first_name= session['previous_first_name'], previous_last_name= session['previous_last_name']);

@app.route('/processregister', methods=["POST"])
def processregister():
    valid = True
    if len(request.form['first_name']) < 2:
        flash("*First Name cannot be empty.")
        valid = False
    if len(request.form['last_name']) < 2:
        flash("*Last Name cannot be empty.")
        valid = False
    if not PASSWORD_REGEX.match(request.form['password']):
        flash("*Password must contain at least 1 capital letter and at least 1 number, and be at least 8 characters long.")
    if request.form['password'] != request.form['confirm_password']:
        flash("*Password inputs must match.")
        valid = False
    if not EMAIL_REGEX.match(request.form['email']):
        flash("*Invalid Email Address.")
        valid = False
    users=mysql.query_db("SELECT * FROM users")
    for user in users:
        if user['email'] == request.form['email']:
            flash("*User already exists!")
            valid = False
            break
    if valid:
        session['previous_email'] = ""
        session['previous_first_name'] = ""
        session['previous_last_name'] = ""
        query = "INSERT INTO users (email, first_name, last_name, password) VALUES (:email, :first_name, :last_name, :password)" 
        data = {
            'email': request.form['email'], 
            'first_name': request.form['first_name'], 
            'last_name': request.form['last_name'],
            'password': md5.new(request.form['password']).hexdigest()
            }
        mysql.query_db(query, data)
        users=mysql.query_db("SELECT * FROM users")
        for user in users:
            if user['email'] == request.form['email']:
                session['logged_in'] = user 
        return redirect('/userpage')
    else:
        session['previous_email'] = request.form['email']
        session['previous_first_name'] = request.form['first_name']
        session['previous_last_name'] = request.form['last_name']
        return redirect('/register')    

@app.route('/login')
def login():
    if 'previous_email' not in session:
        session['previous_email'] = ""
    return render_template("login.html", previous_email= session['previous_email'])

@app.route('/processlogin', methods=["POST"])
def processlogin():
    users=mysql.query_db("SELECT * FROM users")
    for user in users:
        if user['email'] == request.form['email'] and user['password'] == md5.new(request.form['password']).hexdigest():
            session['previous_email'] = ""
            session['logged_in'] = user
            return redirect('/userpage')
    flash("*Email or password is incorrect.")
    session['previous_email'] = request.form['email']
    return redirect('/login')


@app.route('/delete')
def delete():
    return render_template("delete.html")

@app.route('/deleteconfirm', methods=['POST'])
def deleteconfirm():
    users=mysql.query_db("SELECT * FROM users")
    for user in users:
        if user['password'] == md5.new(request.form['password']).hexdigest():
            session['logged_in'] = False 
            mysql.query_db("DELETE FROM users WHERE id =" + str(user['id']))
            return redirect('/')
    flash("*Password is incorrect.")
    return redirect('/login')

@app.route('/userpage')
def userpage():
    if "logged_in" not in session or not session['logged_in']:
        return redirect("/")
    return render_template("userpage.html", email=session['logged_in']['email'], first_name=session['logged_in']['first_name'], last_name=session['logged_in']['last_name'], id=session['logged_in']['id'])

@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect('/')

@app.route('/processtext', methods=['POST'])
def processtext():
    if request.form['type'] == "message":
        query = "INSERT INTO messages (message, created_at, updated_at, user_id) VALUES (:text, NOW(), NOW(), :user)"
        data = {
            'text': request.form['text'],
            'user': session['logged_in']['id']
            }
    else:
        query = "INSERT INTO comments (comment, created_at, updated_at, user_id, message_id) VALUES (:text, NOW(), NOW(), :user, :messageid)"
        data = {
            'text': request.form['text'],
            'user': session['logged_in']['id'],
            'messageid': request.form['messageid']  
            }
    mysql.query_db(query, data)
    return redirect("/")

@app.route('/deletetext', methods=['POST'])
def deletetext():
    if request.form['type'] == "message":
        query = "DELETE FROM messages WHERE id = " + request.form['id']
    else:
        query = "DELETE FROM comments WHERE id = " + request.form['id']
    mysql.query_db(query)
    return redirect("/")

app.run(debug=True)

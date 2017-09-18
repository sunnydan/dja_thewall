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
        dbusers = mysql.query_db("SELECT * FROM users")
        dbmessages = mysql.query_db("SELECT * FROM messages")
        dbcomments = mysql.query_db("SELECT * FROM comments")
        tmessages = []
        for dbmessage in dbmessages:
            tmessage = {}
            for dbuser in dbusers:
                if dbuser['id'] == dbmessage['user_id']:
                    tmessage['user'] = dbuser['first_name'] + " " + dbuser['last_name']
            if dbmessage['updated_at'] > dbmessage['created_at']:
                tmessage['timestamp'] = dbmessage['updated_at']
            else:
                tmessage['timestamp'] = dbmessage['created_at']
            tmessage['message'] = dbmessage['message']
            tmessage['id'] = dbmessage['id']
            if dbmessage['user_id'] == session['logged_in']['id']:
                tmessage['deleteable'] = True
            else:
                tmessage['deleteable'] = False
            tmessage['comments'] = []
            for dbcomment in dbcomments:
                if dbcomment['message_id'] == dbmessage['id']:
                    tcomment = {}
                    for cdbuser in dbusers:
                        if cdbuser['id'] == dbcomment['user_id']:
                            tcomment['user'] = cdbuser['first_name'] + " " + cdbuser['last_name']
                    if dbcomment['updated_at'] > dbcomment['created_at']:
                        tcomment['timestamp'] = dbcomment['updated_at']
                    else:
                        tcomment['timestamp'] = dbcomment['created_at']
                    tcomment['comment'] = dbcomment['comment']
                    tcomment['id'] = dbcomment['id']
                    if dbcomment['user_id'] == session['logged_in']['id']:
                        tcomment['deleteable'] = True
                    else:
                        tcomment['deleteable'] = False
                    tmessage['comments'].append(tcomment)
            tmessages.append(tmessage)
        return render_template("index.html", users=mysql.query_db("SELECT * FROM users"), logged_in=True, email=session['logged_in']['email'], messages=tmessages, user = session['logged_in'])
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
        query = "INSERT INTO users (email, first_name, last_name, password, created_at, updated_at) VALUES (:email, :first_name, :last_name, :password, NOW(), NOW())" 
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
        return redirect('/userpage/'+str(user['id']))
    else:
        session['previous_email'] = request.form['email']
        session['previous_first_name'] = request.form['first_name']
        session['previous_last_name'] = request.form['last_name']
        return redirect('/register') 

@app.route('/updateuser/<userid>')   
def updateuser(userid):
    try:
        user = mysql.query_db("SELECT * FROM users WHERE id = "+str(userid))[0]
    except IndexError:
        return redirect('/')
    return render_template("updateuser.html", user=user);

@app.route('/processupdateuser/<userid>', methods=['POST'])
def processupdateuser(userid):
    try:
        user = mysql.query_db("SELECT * FROM users WHERE id = "+str(userid))[0]
    except IndexError:
        return redirect('/')
    valid = True
    if len(request.form['first_name']) < 2:
        flash("*First Name cannot be empty.")
        valid = False
    if len(request.form['last_name']) < 2:
        flash("*Last Name cannot be empty.")
        valid = False
    if user['password'] != md5.new(request.form['password']).hexdigest():
        flash("*Current Password is incorrect")
        valid = False
    if not PASSWORD_REGEX.match(request.form['new_password']):
        flash("*New Password must contain at least 1 capital letter and at least 1 number, and be at least 8 characters long.")
    if request.form['new_password'] != request.form['confirm_new_password']:
        flash("*New Password inputs must match.")
        valid = False
    if not EMAIL_REGEX.match(request.form['email']):
        flash("*Invalid Email Address.")
        valid = False
    print user['password']
    print request.form['password']
    print md5.new(request.form['password']).hexdigest()
    if valid:
        query = "UPDATE users SET email = '"
        query += request.form['email'] + "', first_name = '"
        query += request.form['first_name'] + "', last_name = '"
        query += request.form['last_name'] + "', password = '"
        query += md5.new(request.form['new_password']).hexdigest() + "', updated_at = NOW() WHERE id = "
        query += str(userid)
        mysql.query_db(query)
        return redirect('/userpage/'+str(user['id']))
    else:
        return redirect('/updateuser/'+str(user['id']))

@app.route('/login')
def login():
    if 'previous_email' not in session:
        session['previous_email'] = ""
    return render_template("login.html", previous_email= session['previous_email'])

@app.route('/processlogin', methods=["POST"])
def processlogin():
    dbusers=mysql.query_db("SELECT * FROM users")
    for user in dbusers:
        if user['email'] == request.form['email'] and user['password'] == md5.new(request.form['password']).hexdigest():
            session['previous_email'] = ""
            session['logged_in'] = user
            return redirect('/userpage/'+str(user['id']))
    flash("*Email or password is incorrect.")
    session['previous_email'] = request.form['email']
    return redirect('/login')


@app.route('/deleteuser/<userid>')
def delete(userid):
    return render_template("delete.html", id=userid)

@app.route('/deleteconfirm/<userid>', methods=['POST'])
def deleteconfirm(userid):
    try:
        user = mysql.query_db("SELECT * FROM users WHERE id ="+str(userid))[0]
    except IndexError:
        return redirect('/')
    if user['password'] == md5.new(request.form['password']).hexdigest():
        messages = mysql.query_db("SELECT * FROM messages WHERE user_id = " + str(user['id']))
        for message in messages:
            mysql.query_db("DELETE FROM comments WHERE message_id = " + str(message['id']))
        mysql.query_db("DELETE FROM messages WHERE user_id =" + str(user['id']))
        if session['logged_in']['id'] == user['id']:
            session['logged_in'] = False
        mysql.query_db("DELETE FROM users WHERE id =" + str(user['id']))
        return redirect('/')
    flash("*Password is incorrect.")
    return redirect('/deleteconfirm/'+str(userid))

@app.route('/users')
def users():
    dbusers = mysql.query_db("SELECT * FROM users")
    return render_template("users.html", users = dbusers)

@app.route('/userpage/<userid>')
def userpage(userid):
    try:
        dbuser = mysql.query_db("SELECT * FROM users WHERE id =" + str(userid))[0]
    except IndexError:
        return redirect('/')
    if session['logged_in']['id'] == dbuser['id']:
        p = True
    else:
        p = False
    return render_template("userpage.html", user = dbuser, permission = p)

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
        mysql.query_db("DELETE FROM comments WHERE message_id = " + str(request.form['id']))
        mysql.query_db("DELETE FROM messages WHERE id = " + str(request.form['id']))
    else:
        #mysql.query_db("DELETE FROM comments WHERE id = " + str(request.form['id']))
        query = "DELETE FROM comments WHERE id = :id"
        data = {
            'id': request.form['id']
        }
        mysql.query_db(query, data)
    return redirect("/")

app.run(debug=True)

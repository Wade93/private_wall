from flask import Flask, render_template, request, redirect, flash, session
from flask_bcrypt import Bcrypt
from mysqlconnection import connectToMySQL
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 

app = Flask(__name__)
app.secret_key = "super secret"
bcrypt = Bcrypt(app)

@app.route('/')
def registration_or_login():
    if 'fname_entry' not in session:
        session['fname_entry'] = ''
    if 'lname_entry' not in session:
        session['lname_entry'] = ''
    if 'email_entry' not in session:
        session['email_entry'] = ''
    return render_template('index.html')

@app.route('/wall')
def successful_login():

    mysql = connectToMySQL("private_wall")
    query = f"SELECT * FROM users WHERE id != {session['userid']};"
    users = mysql.query_db(query)

    mysql = connectToMySQL("private_wall")
    query = f"SELECT first_name, messages.id, content FROM users JOIN messages ON users.id = messages.sender_id WHERE messages.receiver_id = {session['userid']};"
    messages = mysql.query_db(query)
    msg_count = 0
    for i in messages:
        msg_count += 1
    
    mysql = connectToMySQL("private_wall")
    query = f"SELECT COUNT(id) AS 'count' FROM messages WHERE sender_id = {session['userid']};"
    sent_messages = mysql.query_db(query)
    print("------ CHECKING SENT MESSAGES ------")
    print(sent_messages)

    if 'userid' not in session:
        return redirect('/')
    return render_template('wall.html', user_list = users, messages = messages, msg_count = msg_count, sent_count = sent_messages)

@app.route("/username", methods=['POST'])
def username():
    length = False
    found = False
    uname_length = list(request.form['username'])
    if len(uname_length) > 3:
        length = True
    mysql = connectToMySQL('private_wall')        # connect to the database
    query = "SELECT username from users WHERE users.username = %(user)s;"
    data = { 'user': request.form['username'] }
    result = mysql.query_db(query, data)
    if result:
        found = True
    return render_template('partials/username.html', found=found, length=length)
    # render a partial and return it
    # Notice that we are rendering on a post! Why is it okay to render on a post in this scenario?
    # Consider what would happen if the user clicks refresh. Would the form be resubmitted?

# @app.route("/usersearch")
# def search():
#     print("ENGAGING USERSEARCH")
#     found = False
#     mysql = connectToMySQL("private_wall")
#     query = "SELECT * FROM users WHERE first_name LIKE %%(name)s;"
#     data = {
#         "name" : request.args.get('name') + "%"  # get our data from the query string in the url
#     }
#     results = mysql.query_db(query, data)
#     if results:
#         found = True
#     print("*"*20)
#     print("RESULTS", results)
#     return render_template("success.html", users = results, found=found) # render a template which uses the results

@app.route("/search_bar_results")
def search_results():
    print("WE ARE RUNNING SEARCH_BAR_RESULTS")
    found = False
    mysql = connectToMySQL("private_wall")
    query = "SELECT * FROM users WHERE first_name LIKE %%(name)s;"
    data = {
        "name" : request.args.get('name') + "%"  # get our data from the query string in the url
    }
    print(query)
    results = mysql.query_db(query, data)
    if results:
        found = True
    print("*"*20)
    print("RESULTS", results)
    return render_template("partials/search_results.html", users = results, found=found) # render a template which uses the results

@app.route('/process', methods=['POST'])
def process():
    is_valid = True		# assume True
    if len(request.form['fname']) < 1:
        is_valid = False
        flash("Please enter a first name.", "fname")
    if len(request.form['fname']) > 0:
        if len(request.form['fname']) < 2:
            is_valid = False
            flash("Please enter a valid first name. ( > 2 Characters!)", "fname_val")
    if len(request.form['lname']) < 1:
        is_valid = False
        flash("Please enter a last name.", "lname")
    if len(request.form['lname']) > 0:
        if len(request.form['lname']) < 2:
            is_valid = False
            flash("Please enter a valid last name. ( > 2 Characters!)", "lname_val")
    if len(request.form['email']) < 1:
        is_valid = False
        flash("Please enter your email.", "email_enter")
    if len(request.form['email']) > 0:
        if not EMAIL_REGEX.match(request.form['email']):
            is_valid = False
            flash("Please enter a valid email address.", "email_val")
    mysql = connectToMySQL("private_wall")
    query = "SELECT * FROM users WHERE email = %(email)s;"
    data = { "email" : request.form["email"] }
    result = mysql.query_db(query, data)
    if len(result) > 0:
        is_valid = False
        flash("A user with that email already exists.", "user_exists")
    if len(request.form['pw']) < 1:
        is_valid = False
        flash("Please enter a user_pw.", "pw_enter")
    if len(request.form['pw']) > 0:
        if not re.match(r'^(?=.*[0-9]+.*)(?=.*[a-zA-Z]+.*)[0-9a-zA-Z]{8,}$', request.form['pw']):
            is_valid = False
            flash("Passwords must be a minimum of 8 characters and include at least one Capital(s) and a Number(0-9)", "pw_minimum")
    if len(request.form['pwc']) < 1:
        is_valid = False
        flash("Please confirm your user_pw.", "confirm")
    if len(request.form['pwc']) > 0:
        if request.form['pwc'] != request.form['pw']:
            is_valid = False
            flash("Passwords must match.", "pw_match")
    if not is_valid:
        session['fname_entry'] = request.form['fname']
        session['lname_entry'] = request.form['lname']
        session['email_entry'] = request.form['email']
        return redirect('/')
    else:
        pw_hash = bcrypt.generate_password_hash(request.form['pw']) 
        mysql = connectToMySQL("private_wall")
        query = "INSERT INTO users (first_name, last_name, email, user_pw) VALUES (%(fn)s, %(ln)s, %(email)s, %(password_hash)s);"
        data = {
            "fn": request.form['fname'],
            "ln": request.form['lname'],
            "email": request.form['email'],
            "password_hash": pw_hash
            }
        NewUser = mysql.query_db(query, data)
        mysql = connectToMySQL("private_wall")
        query = f"SELECT * FROM users WHERE id = {NewUser};"
        result = mysql.query_db(query)
        session['userid'] = result[0]['id']
        session['username'] = result[0]['first_name']
        return redirect("/wall")


@app.route('/login', methods=['POST'])
def login():

    mysql = connectToMySQL("private_wall")
    query = "SELECT * FROM users WHERE email = %(email)s;"
    data = { "email" : request.form["email"] }
    result = mysql.query_db(query, data)

    if len(result) > 0:
        if bcrypt.check_password_hash(result[0]['user_pw'],request.form['pw']):
            session['userid'] = result[0]['id']
            session['username'] = result[0]['first_name']
            return redirect('/wall')
    flash("You could not be logged in")
    return redirect("/")

@app.route('/send_message', methods=['POST'])
def send_message():
    mysql = connectToMySQL("private_wall")
    query = "INSERT INTO messages (sender_id, receiver_id, content) VALUES (%(sID)s, %(rID)s, %(msg)s);"
    data = {
        "sID" : session['userid'],
        "rID" : int(request.form["friend_id"]),
        "msg" : request.form["msg_content"]
    }
    mysql.query_db(query,data)
    return redirect('/wall')

@app.route('/delete/<mID>')
def delete_message(mID):
    mysql = connectToMySQL("private_wall")
    query = f"DELETE FROM messages WHERE messages.id = {mID};"
    mysql.query_db(query)
    mysql = connectToMySQL("private_wall")
    query = f"SELECT first_name, messages.id, content FROM users JOIN messages ON users.id = messages.sender_id WHERE messages.receiver_id = {session['userid']};"
    messages = mysql.query_db(query)
    return render_template('/partials/messages.html', messages=messages)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
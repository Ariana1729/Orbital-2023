from flask import Flask, request, redirect, render_template_string, render_template, json, make_response
from markupsafe import escape

import pymongo
client = pymongo.MongoClient("mongodb://mongodb:27017/")
db = client["vuln"]
users = db["users"]
notes = db["notes"]
note_count = notes.count_documents({})

app = Flask(__name__,template_folder="templates")

@app.route('/')
def home():
    return render_template('routes.html', app=app)

@app.route('/XSS1/')
def XSS1():
    name = request.args.get('name', None)
    if name is None:
        return redirect("?name=John Smith")
    return f'''<html>
        <body>
            <p>Hello, {name}!</p>
        </body>
    </html>'''

@app.route('/XSS-safe1/')
def XSSsafe1():
    name = request.args.get('name', None)
    if name is None:
        return redirect("?name=John Smith")
    return f'''<html>
        <body>
            <p>Hello, {escape(name)}!</p>
        </body>
    </html>'''
    return render_template_string('''<html>
        <body>
            <p>Hello, {{name}}!</p>
        </body>
    </html>''',name=name)

@app.route('/XSS2/')
def XSS2():
    sanitize = lambda s:s.replace("<","&lt;").replace(">","&gt;")
    style = request.args.get('style', None)
    if style is None:
        return redirect("?style=background:%23fe9810")
    return f'''<html>
        <body>
            <div style="{sanitize(style)}">
                <p>Your input is sanitized :)</p>
            </div>
        </body>
    </html>'''

@app.route('/SSTI/')
def SSTI():
    name = request.args.get('name', None)
    if name is None:
        return redirect("?name=John Smith")
    return render_template_string(f'''<html>
        <body>
            <p>Hello, {name}!</p>
        </body>
    </html>''')

@app.route("/register/", methods=["GET","POST"])
def register():
    if request.method == "GET":
        return render_template("register.html",error="")
    if request.is_json:
        request.form = request.json
    username = request.form.get("username")
    password = request.form.get("password")
    if users.find_one({"username":username}):
        return render_template("register.html",error="Username already exists")
    users.insert_one({"username":username, "password":password})
    return render_template("register_success.html",username=username)

@app.route('/change_pw/', methods=["GET","POST"])
def change_pw():
    username = request.cookies.get("username", None)
    if username is None:
        return redirect("/login/")
    if request.method == "GET":
        return render_template("change_pw.html",success=False,username=username)
    password = request.form.get("password")
    users.update_one({'username': username}, 
                     {'$set': {'password': password}})
    response = make_response(render_template("change_pw.html",success=True))
    response.set_cookie('username', '', expires=0)
    return response

@app.route("/login/", methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html",error="")
    if request.is_json:
        request.form = request.json # Express.js does this by default!
    username = request.form.get("username")
    password = request.form.get("password")
    if db.users.find_one({
        "username":username,
        "password":password
    }):
        response = make_response(render_template("login_success.html"))
        response.set_cookie("username", username)
        return response

    return render_template("login.html",error="Username or password is incorrect")

@app.route('/logout/', methods=['GET'])
def logout():
    response = make_response(redirect('/login'))
    response.set_cookie('username', '', expires=0)
    return response

@app.route("/notes/")
def list_notes():
    search = request.args.get('search', None)
    username = request.cookies.get("username", None)
    if username:
        query = {"$or": [
            {"author": username},
            {"public": True}
        ]}
    else:
        query = {"public": True}
    if search is not None:
        query["title"] = {'$regex': f'.*{search}.*', '$options': 'i'}
    nls = [i for i in notes.find(query)]
    return render_template('list_notes.html', notes=nls, username=username)

@app.route("/read_note/")
def read_note():
    username = request.cookies.get("username", None)
    nid = request.args.get('id', None)
    if nid is None:
        return redirect("/notes/")
    try:
        nid = int(nid)
    except:
        return redirect("/notes/")
    note = notes.find_one({"id":nid})
    return render_template('note.html', note=note, username=username)

@app.route("/add_note/", methods=['GET', 'POST'])
def add_note():
    username = request.cookies.get("username", None)
    if username is None:
        return redirect("/login")
    if request.method == 'GET':
        return render_template('add_note.html', message="", username=username)
    elif request.method == 'POST':
        global note_count
        data = request.form
        note_count += 1
        db.notes.insert_one({
            'id': note_count,
            'author': username,
            'public': bool(data.get('public')),
            'title': data['title'],
            'desc': data['desc']
        })
        return render_template('add_note.html', message='Note added successfully', username=username)

if __name__ == '__main__':
    app.run(host='0.0.0.0')

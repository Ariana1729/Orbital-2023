from flask import Flask, request, redirect, render_template_string, render_template, json
from markupsafe import escape

import pymongo
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["vuln"]
users = db["users"]
notes = db["notes"]

app = Flask(__name__,template_folder="templates")

@app.route('/')
def home():
    routes = []
    html_response = '<html><body>'
    html_response += '<h1>List of Routes:</h1>'
    html_response += '<ul>'
    for rule in app.url_map.iter_rules():
        if rule.endpoint == 'static': continue
        html_response += f'<li><a href="{rule.rule}">{rule.rule}</a></li>'
    html_response += '</ul>'
    html_response += '</body></html>'

    return html_response

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
        return redirect("?style=background%23fe9810")
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
    print(username,password)
    if db.users.find_one({"username":username}):
        return render_template("register.html",error="Username already exists")
    db.users.insert_one({"username":username, "password":password})
    return render_template("register_success.html",username=username)

@app.route("/login/", methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html",error="")
    if request.is_json:
        request.form = request.json
    username = request.form.get("username")
    password = request.form.get("password")
    print(username,password)
    if db.users.find_one({"username":username, "password":password}):
        return render_template("login_success.html")
    return render_template("login.html",error="Username or password is incorrect")

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(debug=True,host='0.0.0.0') # this exposes the server!

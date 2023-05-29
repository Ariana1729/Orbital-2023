from flask import Flask, request, redirect, render_template_string, escape

app = Flask(__name__)

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
    return f'''<html>
        <body>
            <div style="{sanitize(style)}">
                <p>Your input is sanitized :)</p>
            </div>
        </body>
    </html>'''

if __name__ == '__main__':
    app.run(debug=True)

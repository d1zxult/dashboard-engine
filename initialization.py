from flask import render_template
from configuration import create_app

app, resources_handler, compatibility_core = create_app()

@app.route('/')
def index():
    return render_template('auth.html')

@app.route('/terminal')
def terminal():
    return render_template('terminal.html')

@app.route('/overview')
def overview():
    return render_template('overview.html')

@app.route('/explorer')
def explorer():
    return render_template('explorer.html')

@app.route('/modules')
def modules():
    return render_template('modules.html')

@app.route('/settings')
def setting():
    return render_template('settings.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

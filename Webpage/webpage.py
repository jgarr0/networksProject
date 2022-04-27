from flask import render_template, Flask, request

app = Flask(__name__, template_folder='template')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new-message')
def new_message():
    return render_template('new_message.html')

if __name__ == "__main__":
    app.run(debug=True)

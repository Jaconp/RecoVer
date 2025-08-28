import os
import flask
from flask import Flask, render_template

# Create a simple app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "fallback-secret-key-for-development")

# Basic route
@app.route('/')
def home():
    return render_template('index.html', title="Lost and Found")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
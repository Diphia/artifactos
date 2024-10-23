from flask import Flask, request, send_file, abort
import os
from werkzeug.utils import secure_filename
from functools import wraps
import yaml  

app = Flask(__name__)

with open('/etc/artifactos/config.yaml', 'r') as f:
    config = yaml.safe_load(f)
app.config.update(config)

UPLOAD_FOLDER = '/data'

def require_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token != f"Bearer {app.config['TOKEN']}":
            abort(401)
        return f(*args, **kwargs)
    return decorated_function

def require_token_in_query(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.args.get('token')
        if token != app.config['TOKEN']:
            abort(401)
        return f(*args, **kwargs)
    return decorated_function

@app.route('/upload', methods=['POST'])
@require_token
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        return f"File uploaded. Access it at: /data/{filename}", 201

@app.route('/data/<filename>', methods=['GET'])
@require_token_in_query
def get_artifact(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path)
    return 'File not found', 404

if __name__ == '__main__':
    app.run(debug=True)


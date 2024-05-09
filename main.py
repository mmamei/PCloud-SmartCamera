from flask import Flask,request,redirect,url_for,render_template,send_file
from flask_login import LoginManager, current_user, login_user, logout_user, login_required, UserMixin
from secret import secret_key
from google.cloud import firestore
from google.cloud import storage
import json
from datetime import datetime
import os

class User(UserMixin):
    def __init__(self, username):
        super().__init__()
        self.id = username
        self.username = username

app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key
login = LoginManager(app)
login.login_view = '/static/login.html'

usersdb = {
    'marco':'mamei'
}

@login.user_loader
def load_user(username):
    if username in usersdb:
        return User(username)
    return None

@app.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('/sensors'))
    username = request.values['u']
    password = request.values['p']
    if username in usersdb and password == usersdb[username]:
        login_user(User(username))
        return redirect('/sensors')
    return redirect('/static/login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')



@app.route('/cam',methods=['GET'])
def get_camera():
    return redirect('/static/camera.html')


@app.route('/cam',methods=['GET'])
def main():
    return 'ciao'


db = 'sensors'
coll = 'data'
db = firestore.Client.from_service_account_json('credentials.json', database=db)
storage_client = storage.Client.from_service_account_json('credentials.json')


@app.route('/upload/<camera>',methods=['POST'])
def upload(camera):
    # check if the post request has the file part
    file = request.files['file']
    now = datetime.now()
    current_time = now.strftime('%Y_%m_%d_%H_%M_%S')
    bucket = storage_client.bucket('upload-smart-camera')
    blob = bucket.blob(f'{camera}-{current_time}')
    blob.upload_from_string(file.read(), content_type=file.content_type)
    return 'saved'


@login_required
@app.route('/frames/<camera>',methods=['GET'])
def frames(camera):

    blobs = storage_client.list_blobs('upload-smart-camera', prefix=camera)
    blobs = [b.name for b in blobs]
    print(blobs)
    fname = blobs[-1]
    bucket = storage_client.bucket('upload-smart-camera')
    blob = bucket.blob(fname)
    blob.download_to_filename(f'tmp/{fname}.png')
    return send_file(f'tmp/{fname}.png')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=222, debug=True,ssl_context='adhoc')
    print('ciao')


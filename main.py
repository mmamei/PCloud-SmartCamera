from flask import Flask,request,redirect,url_for,render_template,send_file
from flask_login import LoginManager, current_user, login_user, logout_user, login_required, UserMixin
from secret import secret_key
from google.cloud import firestore
from google.cloud import storage
import json
from datetime import datetime
import os
from google.cloud import vision

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


@app.route('/')
def main():
    return 'ciao'


@app.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('/'))
    username = request.values['u']
    password = request.values['p']
    if username in usersdb and password == usersdb[username]:
        login_user(User(username))
        return redirect('/')
    return redirect('/static/login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')



@app.route('/cam',methods=['GET'])
def get_camera():
    return redirect('/static/camera.html')

db_client = 'sensors'
coll = 'camera'

db_client = firestore.Client.from_service_account_json('credentials.json', database=db_client)
storage_client = storage.Client.from_service_account_json('credentials.json')
vision_client = vision.ImageAnnotatorClient.from_service_account_json('credentials.json')

@app.route('/upload/<camera>',methods=['POST'])
def upload(camera):
    # check if the post request has the file part
    file = request.files['file']
    now = datetime.now()
    current_time = now.strftime('%Y_%m_%d_%H_%M_%S')
    bucket = storage_client.bucket('upload-smart-camera')
    blob = bucket.blob(f'{camera}-{current_time}')
    blob.upload_from_string(file.read(), content_type=file.content_type)

    image = vision.Image()
    image.source.image_uri = f'gs://upload-smart-camera/{camera}-{current_time}'
    response = vision_client.face_detection(image=image)
    faces = response.face_annotations
    print('Faces', len(faces))

    id = f'{camera}-{current_time}'
    doc_ref = db_client.collection(coll).document(id)
    doc_ref.set({'cam': camera, 'date':current_time, 'num':len(faces)})
    #print(doc_ref.get().id)

    return 'saved'

@login_required
@app.route('/frames/<camera>/<date>',methods=['GET'])
def frames(camera, date):

    #blobs = storage_client.list_blobs('upload-smart-camera', prefix=camera)
    #blobs = [b.name for b in blobs]
    #print(blobs)
    # cam1-2024_05_09_11_37_50
    fname = f'{camera}-{date}'
    bucket = storage_client.bucket('upload-smart-camera')
    blob = bucket.blob(fname)
    blob.download_to_filename(f'/tmp/{fname}.png')
    return send_file(f'/tmp/{fname}.png')



@app.route('/cam_data/<cam>',methods=['GET'])
def get_data(cam):
    r = []
    for doc in db_client.collection(coll).where('cam', '==', cam).stream():
        print(f'{doc.id} --> {doc.to_dict()}')
        r.append([doc.to_dict()['date'],doc.to_dict()['num']])
    return json.dumps(r)

@app.route('/graph/<cam>', methods=['GET'])
def graph(cam):
    print('ciao2')
    d2 = json.loads(get_data(cam))
    ds = '' # ['2004',  1000,      null],

    for date,val in d2:
        ds += f"['{date}','/frames/{cam}/{date}',{val}],\n"

    print(ds)
    return render_template('graph.html',data=ds)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=222, debug=True,ssl_context='adhoc')
    print('ciao')


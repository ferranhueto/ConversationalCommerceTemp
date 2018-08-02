import base64
import json
import os.path
import zipfile
from functools import wraps
import vobject

import dropbox
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from passlib.hash import sha256_crypt
from werkzeug.utils import secure_filename
from flask_cors import CORS

from dbconnection import adduser, check, check_login, get_videos, get_slides, get_id, \
    activities_db, activity, get_structure1, section_finder, get_chapter, get_section1, find_id
import alexa_database_actions as alexa_db

app = Flask(__name__)
DATABASE = "users.db"
app.secret_key = os.environ["SECRET_KEY"]
app.config['UPLOAD_FOLDER'] = 'static/Content'

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

CORS(app)  # Enable cross-origin resource sharing

# For Dropbox
__TOKEN = os.environ["dbx_access_token"]
__dbx = None


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap


@app.route("/",methods=["GET"])
def home():
    return render_template("welcome.html")


@app.route("/login", methods=["GET","POST"])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if len(username) is 0 or len(password) is 0:
            error="Please fill out both fields."
            return render_template('login.html', error=error)
        l = check_login(username)
        if l is not None:
            if sha256_crypt.verify(password,l):
                m = get_id(username)
                session['logged_in'] = m
                return redirect('/IoT/1/1/1')
        error = "Invalid credentials. Please try again."

    return render_template('login.html', error=error)


@app.route("/signup", methods=["GET","POST"])
def registration():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm']

        if password != confirm:
            error = 'Your passwords are not the same. Please try again'

        password = sha256_crypt.encrypt(str(password))

        x = check("username",username)
        m = check("email",email)

        if x is not 0:
            error = "This username is already being used."

        if m is not 0:
            error = "This email is already assigned to an account."

        if error is None:
            adduser(username, email, password)
            a = get_id(username)
            activities_db(a)
            flash("You are now signed up! Please log in")
            return redirect(url_for('login'))

    return render_template("signup.html", error=error)


@app.route("/logout")
@login_required
def logout():
    session.pop('logged_in', None)
    flash("You were just logged out!")
    return redirect(url_for('home'))


@app.route("/edit", methods=["GET","POST"])
@login_required
def edition():
    if request.method == 'POST':
        pid = request.json['pid']
        id = request.json['id']
        action = request.json['action']
        user = session['logged_in']
        activity_type = request.json['activity_type']
        if activity_type is 1:
            activity_type = 'Section'
            id = find_id(activity_type, id)
        elif activity_type is 2:
            activity_type = 'Chapter'
            id = find_id(activity_type, id)


        activity(user, action, id, pid, activity_type)

    return json.dumps({'status': 'OK'})


@app.route("/upload", methods=["GET","POST"])
@login_required
def upload():
    if request.method == 'POST':
        if 'video-upload' in request.files:
            file = request.files['video-upload']
        else:
            file = request.files['image-upload']

        filename = id()
        upload_folder = url_for('static') + '/Content/IoT/Activities'
        file.save(os.path.join(upload_folder, filename))
        pid = request.json['pid']
        activity_type = request.json['activity_type']
        action = request.json['action']
        user = session['logged_in']

        activity(user, action, pid, filename, activity_type)

    return json.dumps({'status': 'OK'})

@app.route("/save", methods=["GET","POST"])
@login_required
def save():
    img = request.json['title']
    img = img.replace('data:image/png;base64,', '')
    img = img.replace(' ', '+')
    fileData = base64.b64decode(img)
    fileName = '/template/untitled/static/User_Flashcards/photo.png'
    with open(fileName, 'wb') as f:
        f.write(img)
        f.close()
    m = {'success': True}

    return redirect(url_for('safe'))


def __dbx_conn__():
    """ Function returns a connection to Dropbox """
    global __dbx
    if __dbx is None:
        __dbx = dropbox.Dropbox(__TOKEN)
    return __dbx


@app.route("/save_to_dbx")
@login_required
def save_to_dbx():
    """ Saves a course to Dropbox as a .zip """
    # Creating a .zip file out of the course
    zip = zipfile.ZipFile("IoT.zip", "w")
    for subdir, dirs, files in os.walk(os.path.join(BASE_PATH, "static/Content/IoT")):
        for file in files:
            complete__file_path = os.path.join(subdir, file)
            print("Writing to Zip:", complete__file_path)
            zip.write(complete__file_path, complete__file_path.split("/")[-1])
    zip.close()

    # Uploading the .zip to Dropbox
    f = open(os.path.join(BASE_PATH, "IoT.zip"))
    file_size = os.path.getsize(os.path.join(BASE_PATH, "IoT.zip"))

    CHUNK_SIZE = 4 * 1024 * 1024

    print("Upload file size:", file_size)

    if file_size <= CHUNK_SIZE:
        print(__dbx_conn__().files_upload(f, "/VOSW-Backup-Testing/IoT.zip"))
    else:
        upload_session_start_result = __dbx_conn__().files_upload_session_start(f.read(CHUNK_SIZE))
        cursor = dropbox.files.UploadSessionCursor(
            session_id=upload_session_start_result.session_id,
            offset=f.tell())
        commit = dropbox.files.CommitInfo(path="/VOSW-Backup-Testing/IoT.zip")

        while f.tell() < file_size:
            if ((file_size - f.tell()) <= CHUNK_SIZE):
                print(__dbx_conn__().files_upload_session_finish(f.read(CHUNK_SIZE), cursor, commit))
            else:
                __dbx_conn__().files_upload_session_append_v2(f.read(CHUNK_SIZE), cursor)
                cursor.offset = f.tell()

    return """<!DOCTYPE html>
              <html lang="en">
              <head>
                <meta charset="UTF-8">
                <title>Success!</title>
              </head>
              <body>
                <h1>Success!</h1>
              </body>
              </html>"""


@app.route("/upload_course", methods=["GET", "POST"])
@login_required
def upload_course():
    if request.method == 'POST':
        f = request.files['zipfile']
        print(f)
        if f and f.filename[-4:].lower() == '.zip':
            filename = secure_filename(f.filename)
            print(filename)
            p = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(p)
            f.save(p)
            print('saved properly!')
            zip_ref = zipfile.ZipFile(p, 'r')
            zip_ref.extractall(p.rstrip('.zip'))
            zip_ref.close()
            print('folder unzipped!')
            os.remove(p)
            print('zip folder deleted.')
            return """<!DOCTYPE html>
                      <html lang="en">
                      <head>
                        <meta charset="UTF-8">
                        <title>Success!</title>
                      </head>
                      <body>
                        <h1>Success!</h1>
                      </body>
                      </html>"""
        else:
            flash('some error occurred', category='nav-top')
    return render_template('upload_course.html')


@app.route("/IoT/<int:chapter>/<int:section>/<int:m>")
@login_required
def display(chapter, section, m):

    user = session['logged_in']
    structure = get_structure1(user)
    g = section_finder(structure, section, chapter)
    p = '/static/Content/IoT/Activities/'
    l = get_videos(g, user)
    s = get_slides(g, user)
    slides = []
    for c in s:
        slides.append(p + str(c) + '.jpg')

    video = p + str(l[m - 1]) + '.mp4'
    vidcount = len(l)

    return render_template("general_course1.html", section=section, chapter=chapter, video=video, m=m, l=l,
                           vidcount=vidcount, source=slides, structure=map(json.dumps, structure))


@app.route("/IoT/edit", methods=['GET','POST'])
@login_required
def edit():
    user = session['logged_in']
    structure = get_structure1(user)
    structure = get_chapter(structure)

    return render_template("editor.html", structure=map(json.dumps, structure))


@app.route("/IoT/edit/<chapter>", methods=['GET','POST'])
@login_required
def edit_chapter(chapter):
    user = session['logged_in']
    structure = get_structure1(user)
    structure = get_section1(structure, chapter)
    pid = find_id('Chapter', structure[0])
    list=[]
    for s in structure:
        if s is not 'C123':
            list.append(s)

    del list[0]
    structure = list
    return render_template("editor_chapter.html", structure=map(json.dumps, structure), pid=pid)


@app.route("/IoT/edit/<int:chapter>/<int:section>", methods=['GET','POST'])
@login_required
def edit_section(chapter,section):
    user = session['logged_in']
    structure = get_structure1(user)
    g = section_finder(structure, section, chapter)
    pid = find_id('Section', g)
    videos = get_videos(g, user)
    slides = get_slides(g, user)
    s = g
    c = get_chapter(structure)
    c = c[int(chapter)-1]

    return render_template("editor_section.html", videos=videos, slides=slides, chapter=chapter, section=section, s=s, c=c, pid=pid)


#************************************************************************#
#************************************************************************#
#******************** BEGINNINGS OF VCARD STUFF *************************#
#************************************************************************#
#************************************************************************#


@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    """
    Creates a new user in the user_profiles table and active_sessions table

    :return: a JSON indicating success or failure; {"status": True} {"status": False} respectively
    """
    try:
        uuid = alexa_db.create_new_user()
        return jsonify({"status": True, "uuid": uuid})
    except Exception as e:
        print('error while creating new user:', e)
        return jsonify({"status": False})


@app.route('/get_question_json', methods=['GET', 'POST'])
def get_question_json():
    """
    Returns a question from the database in a JSON format

    :return: a json object containing the details of the question
    """
    uuid = request.args.get('uuid')  # the uid of the user querying the server for a question
    quid = alexa_db.lookup_users_current_quid(uuid)

    if quid != "--NONE--":
        vCard_file = open(("/test_vCards/%s.vcf" % quid), "r")
        vCard = vobject.readOne(vCard_file)
        response = {"status": True, "data": {}}
        response["data"]["quid"] = vCard.quid.value
        response["data"]["next_quid"] = vCard.next_quid.value
        response["data"]["prev_quid"] = vCard.prev_quid.value
        response["data"]["question"] = vCard.question.value
        response["data"]["answer"] = [answer.value for answer in vCard.answer_list]
        return jsonify(response)
    else:
        return jsonify({"status": False})


@app.route('/get_question_vcard', methods=['GET', 'POST'])
def get_question_vcard():
    """
    Returns a question from the database in a vCard format

    :return: a json object containing the details of the question
    """
    uuid = request.args.get('uuid')  # the uid of the user querying the server for a question
    quid = alexa_db.lookup_users_current_quid(uuid)
    if quid != "--NONE--":
        return send_file(("/test_vCards/%s.vcf" % quid))


@app.route('/send_answers', methods=['GET', 'POST'])
def send_answers():
    """
    Gets the answers to a series of questions split between those that are correct and wrong

    :return: a JSON response, true if the data was successfully recorded, else false
    """
    try:
        uuid = request.args.get('uuid', type=str)  # the uid of the user taking the quiz
        quid = request.args.get('quid', type=str)  # the uid of the question the user answered
        time = request.args.get('time', type=int)  # estimated time taken for a user to answer
        answer_given = request.args.get('answer_given', type=str)  # the answer given for question

        alexa_db.record_user_answer(uuid, quid, time, answer_given)

        return jsonify({"status": True})

    except ValueError:
        return jsonify({"status": False})


@app.route('/get_results', methods=['GET'])
def get_results():
    """
    Gets the results of a user's performance on the proficiency test

    :return: a JSON response with the number of questions asked and the number of questions the user
             answered correctly
    """
    uuid = request.args.get('uuid', type=str)
    return jsonify(alexa_db.lookup_quiz_results(uuid))


def vCard_tree(quid, spaces=0):
    """
    Displays the vCards in a tree structure for easy viewing.

    :param quid: the current root of a subtree
    :param spaces: the number of spaces to give to the tree's root
    """
    vCard = vobject.readOne(
        open(os.path.join("/test_vCards/", (quid + ".vcf")), "r"))
    print ("-" * spaces) + "| " + vCard.question.value + " (" + vCard.quid.value + ")"
    next_level = {next_q.value for next_q in vCard.next_quid_list}
    [vCard_tree(q, spaces + 2) for q in next_level if q != "--NONE--"]


if __name__ == '__main__':
    app.run(port=8000, threaded=True, host=('0.0.0.0'), ssl_context=('static/cert.pem', 'static/key.pem'))
    #app.run(host=('0.0.0.0'), port=80, debug=False, threaded=True)

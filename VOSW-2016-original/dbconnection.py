import sqlite3
import os.path
import random
import datetime
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "users.db")
activities_path = os.path.join(BASE_DIR, "Activities.db")

def adduser(username1, email1, password1):
    with sqlite3.connect(db_path) as connection:
        c = connection.cursor()
        uid = id()
        c.execute("INSERT INTO users (id,username,email,password) VALUES(?, ?, ?, ?)", (uid, username1,email1,password1))


def check(type,y):
    with sqlite3.connect(db_path) as connection:
        c = connection.cursor()
        t = (y,)
        if type is "username":
            c.execute("SELECT COUNT(*) FROM users WHERE username=?", t)
            l = c.fetchone()
            return int(l[0])

        if type is "email":
            c.execute("SELECT COUNT(*) FROM users WHERE email=?", t)
            d = c.fetchone()
            return int(d[0])

        return None


def check_login(username):
    with sqlite3.connect(db_path) as connection:
        t=(username,)
        c = connection.cursor()
        c.execute("SELECT password FROM users WHERE username=?", t)
        l = c.fetchone()
        if l is None:
            return None
        else:
            return l[0]


def get_id(username):
    with sqlite3.connect(db_path) as connection:
        c = connection.cursor()
        t = (username,)
        c.execute("SELECT id FROM users WHERE username=?", t)
        l = c.fetchone()
        return l[0]


def get_username(info):
    with sqlite3.connect(db_path) as connection:
        c = connection.cursor()
        t = (info,)
        c.execute("SELECT username FROM users WHERE id=?", t)
        l = c.fetchone()
        return l[0]


def get_videos(section, user):
    with sqlite3.connect(activities_path) as connection:
        c = connection.cursor()

        # if user is '35445766':
        #    table = 'activities'
        # else:
        #    table = 'u' + str(user)
        table = 'activities'

        p = []
        step = 1
        previous_id = 0

        c.execute("SELECT id FROM " + table + " WHERE Section_Name='" + section + "' ORDER BY Timestamp DESC LIMIT 1")
        section = c.fetchone()

        section = section[0]

        while step is 1:
            c.execute("SELECT id FROM " + table + " WHERE activity_type='Video' AND Previous_Id=" +
                      str(previous_id) + " AND Parent_Id=" + str(section) + " ORDER BY Timestamp DESC LIMIT 1")
            l = c.fetchone()

            if l is None:
                step = 0
                break

            l = l[0]
            p.append(l)
            previous_id = l

        return p


def get_slides(section, user):
    with sqlite3.connect(activities_path) as connection:
        c = connection.cursor()
        # if user is '35445766':
        #    table = 'activities'
        # else:
        #    table = 'u' + str(user)
        table = 'activities'

        p = []
        step = 1
        previous_id = 0
        c.execute("SELECT id FROM " + table + " WHERE Section_Name='" + section + "' ORDER BY Timestamp DESC LIMIT 1")
        section = c.fetchone()
        section = section[0]
        while step is 1:
            c.execute("SELECT id FROM " + table + " WHERE activity_type='Slide' AND Previous_Id=" +
                      str(previous_id) + " AND Parent_Id=" + str(section) + " ORDER BY Timestamp DESC LIMIT 1")
            l = c.fetchone()

            if l is None:
                step = 0
                break

            l = l[0]
            p.append(l)
            previous_id = l

        return p


def check_id(a):
    with sqlite3.connect(activities_path) as connection:
        c = connection.cursor()

        c.execute("SELECT * FROM activities WHERE id="+str(a))
        l = c.fetchone()
        if l is None:
            return True

        return False


def get_chapter(structure):
    c = 0
    chapter = []
    for s in structure:
        if c is 1:
            chapter.append(s)
        if s is 'C123':
            c = 1
        else: c = 0

    return chapter


def get_section1(structure,chapter):

    sections = []
    c = 0
    m = int(chapter)
    a = 0

    for s in structure:

        a += 1

        if c is m:
            sections.append(s)

        if s is 'C123':
            c += 1

    return sections


def activities_db(user):
    with sqlite3.connect(activities_path) as connection:
        c = connection.cursor()
        c.execute("CREATE TABLE u"+str(user)+" AS SELECT * FROM Activities")


def id():
    m = 1
    while m is not 0:
        a = random.randrange(10000000,99999999)
        if check_id(a):
            m = 0

    return a


def get_structure1(user):
    with sqlite3.connect(activities_path) as connection:
        #if user is '35445766':
        #    table = 'activities'
        #else:
        #    table = 'u' + str(user)
        table = 'activities'
        c = connection.cursor()
        structure = []
        step = 1
        previous_id = 0

        while step == 1:
            sentence = "SELECT Chapter_Name FROM "+table+" WHERE activity_type='Chapter' AND Previous_Id =" + \
                       str(previous_id) + ' ORDER BY Timestamp DESC LIMIT 1'

            c.execute(sentence)
            l = c.fetchone()

            if l is None:
                step = 0
                break

            l = l[0]
            structure.append('C123')
            structure.append(l)
            c.execute('SELECT id FROM ' + table + ' WHERE Previous_Id=' +
                      str(previous_id) + ' AND activity_type="Chapter" ORDER BY Timestamp DESC LIMIT 1')
            previous_id = c.fetchone()

            previous_id = previous_id[0]
            previous_id2 = '0'
            step2 = 1
            while step2 is 1:
                c.execute("SELECT Section_Name FROM "+table+" WHERE Previous_Id=" + str(previous_id2) +
                          " AND Parent_Id="+ str(previous_id) + " ORDER BY Timestamp DESC LIMIT 1")
                l = c.fetchone()
                if l is None:
                    step2 = 0
                    break

                l = l[0]
                structure.append(l)
                c.execute("SELECT id FROM " + table + " WHERE Previous_Id=" + str(previous_id2) +
                          " AND Parent_Id=" + str(previous_id) + " ORDER BY Timestamp DESC LIMIT 1")
                previous_id2 = c.fetchone()[0]

    return structure


def section_finder(structure, section, chapter):
    g = 0
    h = 0
    lock = 'closed'
    for t in structure:
        if g is chapter:
            lock = 'open'

        if t is 'C123':
            g += 1

        if lock is 'open':
            if h is section:
                return t
            h += 1

    return 'Nothing'


def activity(user, action, pointer, pid, activity_type):
    # Connect to the user's database
    # if user is '35445766':
    #    table = 'activities'
    # else:
    #    table = 'u' + str(user)

    table = 'activities'
    with sqlite3.connect(activities_path) as connection:
        c = connection.cursor()

        timestamp = int(time.time())
        print(timestamp)

        a = 1
        b = 2
        course_name = 'IoT'
        new_id = id()
        parent_id = pid
        if action is a:
            c.execute(
                "SELECT Previous_Id FROM " + table + " WHERE id='" + str(pointer) + "' ORDER BY Timestamp DESC LIMIT 1")
            p = c.fetchone()
            if p is not None:
                previous_id = p[0]
            else:
                previous_id = 0

            c.execute(
                "SELECT id FROM " + table + " WHERE Previous_Id='" + str(pointer) + "' ORDER BY Timestamp DESC LIMIT 1")
            a = c.fetchone()
            if a is not None:
                pointer = a[0]
            else:
                previous_id = 1

            c.execute(
                "SELECT Chapter_Name FROM " + table + " WHERE id='" + str(pointer) + "' ORDER BY Timestamp DESC LIMIT 1")
            b = c.fetchone()
            if b is not None:
                chapter_name = b[0]
            else:
                chapter_name = 0

            c.execute(
                "SELECT Section_Name FROM " + table + " WHERE id='" + str(
                    pointer) + "' ORDER BY Timestamp DESC LIMIT 1")
            q = c.fetchone()
            if q is not None:
                section_name = q[0]
            else:
                section_name = 0

            c.execute("INSERT INTO "+table+" (id, activity_type, course_name, Section_Name, Chapter_Name, user_id, Parent_Id, Previous_Id, Timestamp) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", (pointer, activity_type, course_name, section_name, chapter_name, user, parent_id, previous_id, timestamp))

        elif action is b:
            c.execute(
                "SELECT id FROM " + table + " WHERE Previous_Id='0' ORDER BY Timestamp DESC LIMIT 1")
            a = c.fetchone()
            if a is not None:
                previous_id = a[0]
                c.execute(
                    "INSERT INTO " + table + " (id, activity_type, course_name, user_id, Parent_Id, Previous_Id, Timestamp) VALUES(?, ?, ?, ?, ?, ?, ?)",
                    (previous_id, activity_type, course_name, user, parent_id, new_id, timestamp))

            c.execute(
                "INSERT INTO " + table + " (id, activity_type, course_name, user_id, Parent_Id, Previous_Id, Timestamp) VALUES(?, ?, ?, ?, ?, ?, ?)",
                (new_id, activity_type, course_name, user, parent_id, 0, timestamp))


def find_id(type, name):
    with sqlite3.connect(activities_path) as connection:
        c = connection.cursor()
        table = 'activities'
        c.execute('SELECT id FROM '+table+' WHERE '+type+'_name="'+name+'"')
        a = c.fetchone()
        return a[0]
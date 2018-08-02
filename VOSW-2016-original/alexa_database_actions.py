import sqlite3
import os
import uuid
import vobject
from random import shuffle

__BASE_DIR = os.path.dirname(os.path.abspath(__file__))
__db_path = os.path.join(__BASE_DIR, "flashcards_database.db")


# <><><><><><><><><><><><><><><><><><><><><><><><>
# ------------ CREATE DATABASE TABLES ------------
# <><><><><><><><><><><><><><><><><><><><><><><><>

def create_all_tables():
    """
    Initializes all the tables needed for the level test in the database.

    This includes:
        - User Profile
        - Questions
        - User Answers
    """
    create_users_table()
    create_question_answers_table()
    create_active_sessions_table()
    create_user_answers_table()


def create_users_table():
    """
    Initializes the `users` table

    :return: True if table was created successfully, else False.
    """
    print("[...] creating table `users`")
    try:
        with sqlite3.connect(__db_path) as conn:
            c = conn.cursor()
            c.execute('''
              CREATE TABLE users
              (
                uuid TEXT PRIMARY KEY NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
              );
            ''')
        print("[OK] `users` table created successfully")
        return True
    except Exception as e:
        print("[ERROR] while creating table `users`:", e)
        return False


def create_question_answers_table():
    """
    Initializes the `question_answers` table.

    :return: True if table was created successfully, else False.
    """
    print("[...] creating `question_answers` table")
    try:
        with sqlite3.connect(__db_path) as conn:
            c = conn.cursor()
            c.execute('''
              CREATE TABLE question_answers
              (
                quid TEXT NOT NULL,
                answer TEXT NOT NULL,
                next_quid TEXT,
                prev_quid TEXT,
                type TEXT
              );
            ''')
        print("[OK] `question_answers` table created successfully")
        return True
    except Exception as e:
        print("[ERROR] while creating table `question_answers`:", e)
        return False


def create_active_sessions_table():
    """
    Initializes the table that keeps track of users' sessions

    :return: True if table was created successfully, else False.
    """
    print("[...] creating active_sessions table")
    try:
        with sqlite3.connect(__db_path) as conn:
            c = conn.cursor()
            c.execute('''
              CREATE TABLE active_sessions
              (
                uuid TEXT PRIMARY KEY NOT NULL,
                current_quid TEXT NOT NULL,
                question_start_time TEXT DEFAULT CURRENT_TIMESTAMP
              );
            ''')
        print("[OK] active_sessions table created successfully")
        return True
    except Exception as e:
        print("[ERROR] while creating table `active_sessions`:", e)
        return False


def create_user_answers_table():
    """
    Initializes the `user_answers` table

    :return: True if table was created successfully, else False.
    """
    print("[...] creating table `user_answers`")
    try:
        with sqlite3.connect(__db_path) as conn:
            c = conn.cursor()
            c.execute('''
              CREATE TABLE user_answers (
                uuid TEXT NOT NULL,
                quid TEXT NOT NULL,
                time INT NOT NULL,
                answer_given TEXT NOT NULL
              );
            ''')
        print("[OK] `user_answers` table created successfully")
        return True
    except Exception as e:
        print("[ERROR] while creating table `user_answers`:", e)
        return False


# <><><><><><><><><><><><><><><><><><><><><><><><>
# --------------- RECORD FUNCTIONS ---------------
# <><><><><><><><><><><><><><><><><><><><><><><><>


def create_new_user():
    """
    Creates a new user with no fields filled in except for uuid and timestamp

    :return: the new uuid created for the user who is joining
    """
    new_uuid = str(uuid.uuid4())
    starting_quid = "1e09ec08-2651-41d1-8cfb-93f4c1ea4bbe"
    print("[...] creating new user", new_uuid)
    with sqlite3.connect(__db_path) as conn:
        c = conn.cursor()
        c.execute('''INSERT INTO users (uuid) VALUES (?);''', (new_uuid,))
        c.execute('''  /* Instantiate an active session so user does not lose their place */
          INSERT INTO active_sessions (uuid, current_quid) VALUES (?, ?);''',
                  (new_uuid, starting_quid))  # quid is the starting question
    print("[OK] successfully created new user", new_uuid)
    return new_uuid


def record_user_answer(uuid, quid, time, answer_given):
    """
    Records a user's answer to a question in the user_answers table and updates their session.

    :param string uuid: a user's unique identifying string
    :param string quid: a question's unique identifying string
    :param int time: the time it took for a user to answer the question in milliseconds
    :param answer_given: the answer that the user gave to the question
    :return: True if user's answers were recorded successfully, else False
    """
    print("[...] recording user %s answer to question %s" % (uuid, quid))
    answer_given_parsed = answer_given.replace("_", " ")
    with sqlite3.connect(__db_path) as conn:
        c = conn.cursor()

        # recording user's answers
        c.execute('''INSERT INTO user_answers (uuid, quid, time, answer_given) 
                      VALUES (?, ?, ?, ?);''', (uuid, quid, time, answer_given_parsed))
        print("[OK] user %s answer to question %s was successfully recorded" % (uuid, quid))

        # update the user's active_session
        print("[...] updating user %s active session" % uuid)
        vCard_file = open(os.path.join((__BASE_DIR + "/test_vCards/"), (quid + ".vcf")), "r")
        vCard = vobject.readOne(vCard_file)
        answers = [answer.value for answer in vCard.answer_list]
        next_quids = [quid.value for quid in vCard.next_quid_list]
        print(">>>>>>>> ANSWER GIVEN:", answer_given_parsed, "<<<<<<<<")
        alphabet_indices = {0: "a", 1: "b", 2: "c", 3: "d"}
        added_to_table = False
        for answer, next_quid in zip(answers, next_quids):
            if (alphabet_indices[answers.index(answer)] == answer_given_parsed) or (
                alphabet_indices[answers.index(answer)] == answer_given_parsed[0:-1]):
                c.execute('''UPDATE active_sessions SET current_quid = ?''', (next_quid,))
                added_to_table = True
                print("[OK] successfully updated user %s to question %s in `active_sessions`" % (
                    uuid, next_quid))
                break
        if not added_to_table:
            random_quid = next_quids
            shuffle(random_quid)
            c.execute('''UPDATE active_sessions SET current_quid = ?''', (random_quid[0],))
            print("[OK] successfully updated user %s to randomly chosen question %s" % (
                uuid, random_quid[0]))


def load_vCard_into_question_answers(vCard):
    """
    Loads a vCard into the `question_answers` database table.

    :param vCard: a vobject that follows the Aba English level test naming standards
                  For more information on vobject see: https://eventable.github.io/vobject/
    """
    quid = vCard.quid.value
    answers = [a.value for a in vCard.contents['answer']]
    next_quids = [q.value for q in vCard.next_quid_list]
    prev_quid = vCard.prev_quid.value
    type = vCard.type.value

    print("[...] loading vCard %s into `question_answers` table" % quid)
    for answer, next_quid in zip(answers, next_quids):
        with sqlite3.connect(__db_path) as conn:
            c = conn.cursor()
            c.execute(''' INSERT INTO question_answers (quid, answer, next_quid, prev_quid, type) 
                          VALUES (?, ?, ?, ?, ?); ''', (quid, answer, next_quid, prev_quid, type))
    print("[OK] successfully loaded vCard %s into `question_answers` table" % quid)


def load_folder_of_vCards_into_question_answers(path):
    """
    Iterates through a directory and loads each vCards relevant information into `question_answers`

    :param path: the path to a directory full of vCards
    """
    for filename in os.listdir(path):
        if filename.endswith(".vcf"):
            vCard_file = open(os.path.join(path, filename), "r")
            vCard = vobject.readOne(vCard_file)
            load_vCard_into_question_answers(vCard)
        else:
            continue


# <><><><><><><><><><><><><><><><><><><><><><><><>
# --------------- LOOKUP FUNCTIONS ---------------
# <><><><><><><><><><><><><><><><><><><><><><><><>


def lookup_users_current_quid(uuid):
    """
    Looks up an attribute for a user in active_sessions.

    :param str uuid: a user's unique identifying string
    :raises ValueError: if attribute could not be found for a given uuid in active_sessions
    :return: the current question the user with uuid = uuid is on according to what
             is listed in active_sessions
    """
    print("[...] looking up current question for user %s in `active_sessions`" % uuid)
    with sqlite3.connect(__db_path) as conn:
        c = conn.cursor()
        c.execute('''SELECT current_quid FROM active_sessions WHERE uuid=?;''', (uuid,))
        result = c.fetchone()
        if result is not None:
            print("[OK] successfully got current question %s for user %s in `active_sessions`" % (
            result[0], uuid))
            return result[0]
        else:
            print("[ERROR] while trying to find question for user %s in ``active_sessions`" % uuid)
            raise ValueError("couldn't find question for user %s in `active_sessions`" % uuid)


def lookup_quiz_results(uuid):
    """
    Looks up the results of a user who has just taken a test.

    Currently, this function assumes that user will only take the exam once.

    :param uuid: the unique identifier of the user who is taking the quiz
    :return: a dictionary of the form {"correct": x, "total": y} where x is the number of questions
             that a user answered correctly on the quiz and y is the total number of proficiency
             questions they answered
    """
    print("[...] looking up quiz results for user", uuid)
    with sqlite3.connect(__db_path) as conn:
        c = conn.cursor()
        c.execute('''SELECT quid, answer_given FROM user_answers WHERE uuid=?;''', (uuid,))
        result = c.fetchall()
        if result is not None:
            print("[OK] successfully got results for user %s from database" % uuid)
            total_questions = 0
            number_correct = 0
            for quid, answer in result:
                if quid != "--NONE--":
                    vCard_file = open((__BASE_DIR + ("/test_vCards/%s.vcf" % quid)), "r")
                    vCard = vobject.readOne(vCard_file)
                    if vCard.type.value == "PROFICIENCY":
                        total_questions += 1
                        correct_answer = [a.value.lower() for a in vCard.correct_answer_list]
                        number_correct += (answer in correct_answer or (answer[0:-1] in correct_answer))
                    elif vCard.type.value == "PROFILE":
                        total_questions += 1
                        number_correct += 1
            response = {"correct": number_correct, "total": total_questions}
            return response
        else:
            print("[ERROR] while trying to find results for user", uuid)
            raise ValueError(("couldn't find results for user " + uuid))
# from __future__ import print_function
import time
import urllib.request
import json


def lambda_handler(event: dict, context: dict) -> dict:
    """
    The entry point to this Python script. This function must be defined in order for AWS to know
    where to pass requests.

    :param event: the request that is sent to the server from the Amazon Echo
    :param context: useful runtime information -- for more information, see:
                    https://docs.aws.amazon.com/lambda/latest/dg/nodejs-prog-model-context.html
    :return: a response JSON that is the Alexa's built response
    """
    print("Python START -------------------------------")
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])
    print("Context:\n", context)

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']}, event['session'])
        # ensure that a user can't jump into the middle of the program
        return on_launch(event['request'], event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request: dict, session: dict) -> None:
    """
    If new session is started this function is called to print out relevant session details.

    :param session_started_request: a request to start a session of this skill
    :param session: information about the session as a whole such as the sessionId
    :return:
    """
    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request: dict, session: dict) -> dict:
    """
    Called when the user launches the skill without specifying what part of the skill they want.

    :param launch_request: a request to launch the skill from the beginning, i.e. the welcome
    :param session: information about the session as a whole such as the sessionId
    :return: a built welcome response JSON created by the get_welcome_response() function
    """
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    return get_welcome_response()


def on_intent(intent_request: dict, session: dict) -> dict:
    """
     Called when the user specifies an intent for this skill.

    :param intent_request: a request JSON containing data about what intent the user is requesting
    :param session: information about the session as a whole such as the sessionId
    :return: the built JSON response that reflects the correct user intent request
    """
    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent['name']
    attributes = session["attributes"] if 'attributes' in session else None
    intent_slots = intent['slots'] if 'slots' in intent else None

    # TODO : Authenticate users

    if intent_name == "AMAZON.YesIntent" and (attributes is None):
        try:  # a try/except block to ensure that if server isn't running there is graceful exit
            return ask_question_with_new_user()
        except:
            return ask_for_restart_response()

    elif intent_name == "AMAZON.NoIntent" and (attributes is None):
        return not_ready_response()

    elif attributes is None:
        # If Yes/NoIntent aren't recognized but they should be, attributes will be None.
        # It thinks that a botched Yes/No is an AnswerIntent so it fails out -- this catches that
        return get_yes_no_reprompt_response()

    elif intent_name == "AnswerIntent":
        return get_answer_response(intent_slots, attributes)

    elif intent_name == "AMAZON.NextIntent":
        return get_next_question(attributes)

    elif intent_name == "AMAZON.RepeatIntent":
        return get_repeat_response(attributes)

    elif intent_name == "AMAZON.HelpIntent":
        return get_help_response()

    else:
        return unidentified_intent_response()


def on_session_ended(session_ended_request: dict, session: dict) -> dict:
    """
    Called when the user ends the session -- not when the skill returns should_end_session=true

    :param session_ended_request: a request to end the current skill
    :param session: information about the session as a whole such as the sessionId
    :return: a built JSON response to gracefully exit the current skill's session
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    return get_session_end_response()


# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# --------------- Functions that control the skill's behavior ------------------
# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>


def get_welcome_response() -> dict:
    """ Returns the welcome message when the user enters the skill """
    session_attributes = {}
    card_title = ""
    speech_output = ("Welcome to the E eleven flash card skill! Please select the best answer " +
                     "by repeating the letter corresponding to your answer of choice. Are you " +
                     "ready?")
    reprompt_text = "Say yes if you are ready to begin."
    should_end_session = False

    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text,
                                                   should_end_session))


def get_results_response(uuid: str) -> dict:
    """
    Gets the user's results for the quiz they completed

    :param str uuid: the unique id of the user who just completed the quiz
    :return: a built response that states the user's placement and answer summary
    """
    url = "http://databrook.mit.edu:8080/get_results?uuid=%s" % uuid
    response = urllib.request.urlopen(url)
    data = json.loads(response.read().decode('utf8'))

    fraction_right_response = str(data["correct"]) + " out of " + str(data["total"])

    session_attributes = {}
    card_title = ""
    speech_output = "You got " + fraction_right_response + " question correct."
    reprompt_text = ''
    should_end_session = True

    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text,
                                                   should_end_session))


def query_server(uuid: str) -> dict:
    """
     Queries the server for questions based on the user's uuid

    :param uuid: the unique identifier of the user to get a question for.
    :return: a JSON where they key "status" either has a value of True or False depending on whether
             querying the server was successful or not. If the query was successful, there is an
             additional key of "data" which contains all the data collected from the server.
    """
    url = "http://databrook.mit.edu:8080/get_question_json?uuid=%s" % uuid
    response = urllib.request.urlopen(url)
    data = json.loads(response.read().decode('utf8'))

    if data["status"]:
        question = data["data"]["question"]
        quid = data["data"]["quid"]
        next_quid = data["data"]["next_quid"]
        prev_quid = data["data"]["prev_quid"]
        answers = data["data"]["answer"]

        return {"status": True,
                "data": {"question": question, "quid": quid, "next_quid": next_quid,
                         "prev_quid": prev_quid, "answers": answers}}
    else:
        return {"status": False}


def ask_question(uuid: str, long_prompt: bool = True) -> dict:
    """
    Returns a quiz question to the user since they specified a QuizIntent

    :param uuid: the unique id of a user taking the quiz
    :param long_prompt: whether or not the user should be given long directions or not corresponding
                        to the parameter types True and False values
    :return: a built question response or a results response if the user previously answered their
             last question
    """
    try:
        question_data = query_server(uuid)
    except:
        return ask_for_restart_response()

    if question_data["status"]:

        card_title = ""
        speech_output = ""
        reprompt_text = ""
        directives = []
        should_end_session = False

        session_attributes = {
            "quid": question_data["data"]["quid"],
            "uuid": uuid,
            "question_start_time": time.time(),
        }
        if not long_prompt:
            session_attributes["asked_long_prompt"] = True

        print("QUID:", question_data["data"]["quid"])
        question = question_data["data"]["question"]
        print("QUESTION:", question)
        answers = question_data["data"]["answers"]  # answers are shuffled when pulled from server
        print("ANSWERS:", answers)

        # Make the Echo say all of the possible answers
        alphabet_indices = {0: "A", 1: "B", 2: "C", 3: "D", 4: "E", 5: "F", 6: "G", 7: "H", 8: "I"}
        answer_letters = [(alphabet_indices[answers.index(answer)], answer) for answer in answers]
        answers_string = ""
        for letter, answer in answer_letters:
            answers_string += (letter + ", " + answer + ". ")  # handle how the answers are said

        speech_output += question + ". " + answers_string
        reprompt_text += "Please say the letter associated with your chosen answer."

        return build_response(session_attributes,
                              build_speechlet_response(card_title, speech_output, reprompt_text,
                                                       should_end_session, directives))
    else:
        return get_results_response(uuid)


def ask_question_with_new_user() -> dict:
    """
    Creates a new user that the server will recognize and whose action will be stored in db

    :return: the response from ask_question according the uuid generated in this function
    """
    url = "http://databrook.mit.edu:8080/create_user"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read().decode('utf8'))
    uuid = data["uuid"]
    return ask_question(uuid)


def get_next_question(attributes: dict) -> dict:
    quid = attributes["quid"]
    uuid = attributes["uuid"]
    answer_given = attributes["answer_given"]

    try:
        time_used_for_question = attributes["time_used_for_question"]
    except KeyError:
        time_used_for_question = 0

    try:
        # server records responses and moves to the next question
        send_quiz_responses_to_server(uuid, quid, time_used_for_question, answer_given)
    except:
        return ask_for_restart_response()

    return ask_question(uuid, False)


def get_repeat_response(attributes: dict) -> dict:
    """
    Repeats the same question that the user just heard. Simply not recording the answer the user
    gave on the server ensures that the question the user is on is not incremented and thus they
    remain on the same question

    :param attributes: a dictionary that carries key:value between interactions with the device;
                       this allows for the emulation of state
    :return: a question response that is the question the user just heard
    """
    uuid = attributes["uuid"]
    return ask_question(uuid, False)


def send_quiz_responses_to_server(uuid: str, quid: str, time_used_for_question: str,
                                  answer_given: str) -> bool:
    """
    Sends the users responses back to the server to be stored in the database

    :param uuid: the unique id of the user that just answered a question
    :param quid: the unique question id of the question the user just answered
    :param time_used_for_question: a rough estimate of the time it took the user to answer the
                                   question, given in time since epoch
    :param answer_given: the raw answer that the user provided to the Alexa. Note: this answer will
                         be cleaned a bit on the server -- it must be as the Alexa has a way of
                         misunderstanding slots occasionally. For example "c four" could be
                         interpreted as "c4"
    :return: True if the data was successfully sent to the server, else False
    """
    answer_no_spaces = answer_given.replace(" ", "_")  # ensure answer grabbed has no spaces
    url = ("http://databrook.mit.edu:8080/send_answers?uuid=%s&quid=%s&time=%s&answer_given=%s" %
           (uuid, quid, time_used_for_question, answer_no_spaces))
    response = urllib.request.urlopen(url)
    data = json.loads(response.read().decode('utf8'))
    return data["status"]


def build_bad_answer_response(answer_given: str, attributes: dict) -> dict:
    """
    Builds up a bad response JSON if the answer the user gave was not understood by the machine as a
    correct answer.

    :param answer_given: the answer the machine interpreted the user as saying
    :param attributes: a dictionary that carries key:value between interactions with the device;
                       this allows for the emulation of state
    :return: a response for if the Alexa did not interpret the user's answer as A, B, C, or D
    """
    attributes["answer_given"] = answer_given

    if answer_given == "None":
        if not attributes["asked_long_prompt"]:
            speech_output = ("I am sorry I didn't understand your answer. If you would like " +
                             "to skip this question please say, next, otherwise say, repeat.")
        else:
            speech_output = "I didn't understand. Please say, next, or repeat"
    else:
        if not attributes["asked_long_prompt"]:
            speech_output = ("I heard you say " + answer_given + " which is not equal to A, B, " +
                             "C, or D. If you would like to skip this question please say, next, " +
                             "otherwise say, repeat.")
        else:
            speech_output = "I heard you say " + answer_given + ". Please say, next, or repeat."
    attributes["asked_long_prompt"] = True  # after this, long prompt should be asked no matter what

    card_title = ""
    reprompt_text = ("Please say, next, to move on to the next question. If you would like to " +
                     "to do this question again, please say, repeat.")
    session_attributes = attributes
    should_end_session = False

    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text,
                                                   should_end_session))


def build_good_answer_response(answer_given: str, attributes: dict) -> dict:
    question_start_time = attributes["question_start_time"]
    answer_chosen_images = attributes["answer_chosen_images"]

    attributes["answer_given"] = answer_given

    answer_key = {"a": 0, "b": 1, "c": 2, "d": 3}

    # calculate a rough estimate of the time it took to answer question (time since epoch)
    time_used_for_question = str(int(time.time() - question_start_time))
    attributes["time_used_for_question"] = time_used_for_question

    if not attributes["asked_long_prompt"]:
        speech_output = ("You answered, " + answer_given + ". If this is the answer you would " +
                         "like, please say, next. if you would like to redo the question, please " +
                         "say, repeat.")
    else:
        speech_output = "You answered, " + answer_given + ". Please say, next, or repeat."
    reprompt_text = ("Please say, next, to move on to the next question. If you would like " +
                     "to do this question again, please say, repeat.")

    attributes["asked_long_prompt"] = True  # after this, long prompt should be asked no matter what
    card_title = ""
    session_attributes = attributes
    should_end_session = False

    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text,
                                                   should_end_session))


def get_answer_response(slots: dict, attributes: dict) -> dict:
    """
    Returns a correct/incorrect message to the user depending on their AnswerIntent

    :param slots: a JSON object that details what the user said to fill a given speech slot
    :param attributes: the attributes that are passed between states of the skill
    :return: a built JSON response corresponding to how a user answered the previous question
    """
    if "asked_long_prompt" not in attributes:
        attributes["asked_long_prompt"] = False

    try:
        answer_given = slots["Answer"]["value"].lower()
    except (TypeError, KeyError):
        # if speech wasn't recognized, ask the user if they are sure that they want to pass...
        return build_bad_answer_response("None", attributes)

    if len(answer_given) == 2 and (answer_given[:-1] in ['a', 'b', 'c', 'd']):
        # this is to catch weird entries like "b." etc.
        return build_good_answer_response(answer_given[:-1], attributes)

    elif len(answer_given) == 1 and (answer_given in ['a', 'b', 'c', 'd']):
        return build_good_answer_response(answer_given, attributes)

    else:
        return build_bad_answer_response(answer_given, attributes)


def get_help_response() -> dict:
    """
     Generates a help message to the user since they called AMAZON.HelpIntent

    :return: a built JSON help response
    """
    session_attributes = {}
    card_title = ""
    speech_output = ("This is the E eleven flash card quiz. Please speak a letter for each " +
                     "question given followed by the answer word or phrase.")
    reprompt_text = "Please give me a letter."
    should_end_session = False

    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text,
                                                   should_end_session))


def get_yes_no_reprompt_response() -> dict:
    """
    Generates a prompt for the user asking them to repeat yes or no

    :return: a built JSON response to get yes or no from a user
    """
    session_attributes = {}
    card_title = ""
    speech_output = "Please answer my question with yes or no."
    reprompt_text = "Say yes if you are ready. Say no if you are not ready."
    should_end_session = False

    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text,
                                                   should_end_session))


def ask_for_restart_response() -> dict:
    """
    Generates a restart message if there is a server-side error

    :return: a built JSON response asking the user to restart the skill
    """
    session_attributes = {}
    card_title = ""
    speech_output = ("There seems to be a server issue on our end. Please try restarting the " +
                     "skill! If the problem persists, please contact customer support.")
    reprompt_text = ''
    should_end_session = True

    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text,
                                                   should_end_session))


def not_ready_response() -> dict:
    """
     Generates a message telling the user to return to the skill later when they are ready

    :return: a built JSON response asking the user to restart the skill
    """
    session_attributes = {}
    card_title = ""
    speech_output = ("Alright. Please restart the skill when you are ready to take the " +
                     "proficiency test.")
    reprompt_text = ''
    should_end_session = True

    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text,
                                                  should_end_session))


def unidentified_intent_response() -> dict:
    """
    Generates a response for the user if what they said fell through all the try/catches

    :return: a build JSON response giving the user an ending message
    """
    session_attributes = {}
    card_title = ""
    speech_output = ("I'm sorry, I just don't understand what you are saying. Maybe try restarting" +
                     " this skill and answering the questions with a letter, followed by the " +
                     "corresponding word or phrase.")
    reprompt_text = ''
    should_end_session = True

    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text,
                                                  should_end_session))


def get_session_end_response() -> dict:
    """
    Generates the ending message if a user errs or exits the skill

    :return: a built JSON response giving the user an ending message
    """
    session_attributes = {}
    card_title = ''
    speech_output = 'Thank you for spending time with E eleven today!'
    reprompt_text = ''
    should_end_session = True

    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text,
                                                  should_end_session))



# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    speechlet_response = {}
    speechlet_response['outputSpeech'] = {'type': 'PlainText', 'text': output}
    speechlet_response['card'] = {'type': 'Simple', 'title': title, 'content': output}
    speechlet_response['reprompt'] = {}
    speechlet_response['reprompt']['outputSpeech'] = {'type': 'PlainText', 'text': reprompt_text}
    speechlet_response['shouldEndSession'] = should_end_session
    return speechlet_response


def build_response(session_attributes, speechlet_response):
    response = {}
    response['version'] = '1.0'
    response['sessionAttributes'] = session_attributes
    response['response'] = speechlet_response
    return response

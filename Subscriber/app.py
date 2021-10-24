from flask import Flask, request, render_template
import requests
import argparse
import copy

app = Flask(__name__)
app.debug = True
messages = []  # Topics
undo_messages = []  # Unsubscribed Topics
entered_undo_messages = []
data = {}
register_flag = False


@app.route('/')
def my_form():
    global register_flag, messages
    print("HITTING WITHOUT")
    if (not register_flag):
        register_flag = True
        requests.post(url='http://central_broker:8990/register_subscriber')

    print('my_form')
    print(messages)
    return render_template("my-form.html", list_to_send=data, notifications=messages,
                           unsubscribe=entered_undo_messages)


@app.route('/', methods=['POST'])
def my_form_post():
    global messages, data, undo_messages, entered_undo_messages
    print("HITTING POST")
    print('my_form_post', messages)
    checkboxes = []
    temp_messages = copy.deepcopy(messages)
    for checkbox in messages:
        # print('topic', checkbox)
        value = request.form.get(checkbox)
        # print(value)
        if value:
            checkboxes.append(checkbox)
            temp_messages.remove(checkbox)

    undo_messages = copy.deepcopy(checkboxes)
    temp_entered_undo_messages = copy.deepcopy(entered_undo_messages)
    undo_checkboxes = []

    for checkbox in entered_undo_messages:
        print('topic', checkbox)
        value = request.form.get(checkbox)
        print(value)
        if value:
            undo_checkboxes.append(checkbox)
            temp_entered_undo_messages.remove(checkbox)

    messages = copy.deepcopy(temp_messages)
    entered_undo_messages = copy.deepcopy(temp_entered_undo_messages)
    print('checkboxes', checkboxes)

    if (checkboxes != []):
        topics = {'topics': checkboxes}

        try:
            requests.post(url='http://central_broker:8990/subscriber/subscribe', params=topics)
        except Exception as e:
            data = {'Error': 'Central Broker Not Found'}
    entered_undo_messages.extend(undo_messages)
    messages.extend(undo_checkboxes)
    undo_messages = []
    # print('entered_undo_messages', entered_undo_messages)
    print('undo_checkboxes', undo_checkboxes)

    if (undo_checkboxes != []):
        undo_topics = {'topics': undo_checkboxes}

        try:
            for topic_unsubs in undo_topics['topics']:
                if topic_unsubs in data:
                    del data[topic_unsubs]
            requests.post(url='http://central_broker:8990/subscriber/unsubscribe', params=undo_topics)
        except Exception as e:
            data = {'Error': 'Central Broker Not Found'}

    return render_template("my-form.html", list_to_send=data, notifications=messages,
                           unsubscribe=entered_undo_messages)


@app.route('/notify', methods=['POST'])
def my_form_notify():
    global messages
    global data

    print('Received Notify')

    advertise_flag = str(request.json['advertise_flag'])
    print(advertise_flag)
    if (advertise_flag == 'no'):
        data = request.json['data']
    else:
        advertise_action = request.json['advertise_action']
        Topics = request.json['topics']
        print("Topics:", Topics)
        if advertise_action.lower() == "advertise":
            if len(messages) == 0:
                messages = Topics
            else:
                for topic in Topics:
                    if topic not in messages:
                        messages.append(topic)
        else:
            for topic in Topics:
                if topic in messages:
                    messages.remove(topic)
                if topic in entered_undo_messages:
                    entered_undo_messages.remove(topic)
                if topic in data:
                    del data[topic]

    return "Received Notify"


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--port", type=str, help="Port on which to start the app")
    argv = parser.parse_args()

    app.run(host = '0.0.0.0', port = argv.port)
    #


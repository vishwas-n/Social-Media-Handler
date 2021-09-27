from flask import Flask, request, render_template, redirect, url_for
import requests
import json

app = Flask(__name__)
app.debug = True

@app.route('/')
def my_form():
    return render_template('my-form.html')


@app.route('/', methods=['POST'])
def my_form_post():
    selection = request.form['Socialmedia']
    print('Selection', selection)

    processed_text = request.form['text']
    print('text', processed_text)

    radio = request.form['radio']
    print('Radio', radio)

    input_dict = {
        "socialmedia": selection,
        "keyword": processed_text,
        "fetchmode": radio
    }


    sample = {}
    try:
        list_object = requests.get(url='http://python-docker_web_1:8990/social_media_handle', params=input_dict)
        #list_object = requests.get(url='http://localhost:8990/social_media_handle', params=input_dict)
        sample = json.loads(list_object.text)
    except Exception as e:
        sample['data'] = ['Server Not Found']
    return render_template("my-form.html", list_to_send=sample['data'])


if __name__ == '__main__':
    app.run()

# @app.route('/')
# def index():
#     return render_template('my-form.html')

# @app.route('/submit', methods=['POST'])
# def submit():
#     return 'You entered: {}'.format(request.form['text'])


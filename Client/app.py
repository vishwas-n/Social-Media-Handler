from flask import Flask, request, render_template, redirect, url_for
app=Flask(__name__)
app.debug = True

solr_dict={
    "data": [
        "@alifarhat79 So Gold is not investable? Well if you had invested invested £3000 in 2007 &amp; held until August 2020 you would be at £15k (5 bagger) in spite of the 08 recession &amp; covid crash. Dont put all your money into 1 asset class agreed. Diversify.. but gold isnt so bad as u make it out 2b",
        "Districts as of 9/17:  8,343 (96%) were offering full in-person learning, 322 (4%) were offering hybrid learning, and 35 (0.4%) were offering full remote learning. \n\n COVID-19–Related School Closures and Learning Modality Changes - CDC https://t.co/eZMOhsvBqT",
        "@CDCgov Correction: COVID-19 vaccines are extremely effective at causing serious illness and death",
        "@machelrillman Twitter needs a \"have you considered cranking off instead of posting\" interrupt like the ones that fire for covid-19 misinfo",
        "@ConsumerSOS LA Covid Lockdown: Scary almost. https://t.co/NuPdjADHBw",
        "Minnesota Department of Health: State prepared for administration of Pfizer COVID boosters https://t.co/ORoloj4W3j",
        "negative at home covid-test ✅ bags packed ✅ checked in for flight ✅ next stop CIN-BWI-PUJ 🤪",
        "Aucklanders urge people to follow the rules: 'Think of the community' https://t.co/YNvau0SCmC",
        "SHOULD YOUR BUSINESS STILL EXHIBIT AT TRADE SHOWS POST-COVID?\nhttps://t.co/IHfcS8sAtC. \nBusiness Expo at Elland Road Leeds 4 Nov 2021 details here: https://t.co/g6dHbdADPj.\n#yorbusiness #marketing https://t.co/1lHh3POdPY",
        "COVID-19 may impair men’s sexual performance https://t.co/ZRJ26y3zvl via @NatGeo Hey, guy, here's one good reason for you to #GetvaccinatedNow!",
        "SHOULD YOUR BUSINESS STILL EXHIBIT AT TRADE SHOWS POST-COVID?\nhttps://t.co/IHfcS8sAtC. \nBusiness Expo at Elland Road Leeds 4 Nov 2021 details here: https://t.co/g6dHbdADPj.\n#yorbusiness #marketing https://t.co/1lHh3POdPY",
        "COVID-19 may impair men’s sexual performance https://t.co/ZRJ26y3zvl via @NatGeo Hey, guy, here's one good reason for you to #GetvaccinatedNow!",
        "SHOULD YOUR BUSINESS STILL EXHIBIT AT TRADE SHOWS POST-COVID?\nhttps://t.co/IHfcS8sAtC. \nBusiness Expo at Elland Road Leeds 4 Nov 2021 details here: https://t.co/g6dHbdADPj.\n#yorbusiness #marketing https://t.co/1lHh3POdPY",
        "COVID-19 may impair men’s sexual performance https://t.co/ZRJ26y3zvl via @NatGeo Hey, guy, here's one good reason for you to #GetvaccinatedNow!",
        "SHOULD YOUR BUSINESS STILL EXHIBIT AT TRADE SHOWS POST-COVID?\nhttps://t.co/IHfcS8sAtC. \nBusiness Expo at Elland Road Leeds 4 Nov 2021 details here: https://t.co/g6dHbdADPj.\n#yorbusiness #marketing https://t.co/1lHh3POdPY",
        "COVID-19 may impair men’s sexual performance https://t.co/ZRJ26y3zvl via @NatGeo Hey, guy, here's one good reason for you to #GetvaccinatedNow!",
        "SHOULD YOUR BUSINESS STILL EXHIBIT AT TRADE SHOWS POST-COVID?\nhttps://t.co/IHfcS8sAtC. \nBusiness Expo at Elland Road Leeds 4 Nov 2021 details here: https://t.co/g6dHbdADPj.\n#yorbusiness #marketing https://t.co/1lHh3POdPY",
        "COVID-19 may impair men’s sexual performance https://t.co/ZRJ26y3zvl via @NatGeo Hey, guy, here's one good reason for you to #GetvaccinatedNow!",
        "SHOULD YOUR BUSINESS STILL EXHIBIT AT TRADE SHOWS POST-COVID?\nhttps://t.co/IHfcS8sAtC. \nBusiness Expo at Elland Road Leeds 4 Nov 2021 details here: https://t.co/g6dHbdADPj.\n#yorbusiness #marketing https://t.co/1lHh3POdPY",
        "COVID-19 may impair men’s sexual performance https://t.co/ZRJ26y3zvl via @NatGeo Hey, guy, here's one good reason for you to #GetvaccinatedNow!"
    ]
}

@app.route("/smallest/")
def small():
    return "Fuck man"

@app.route('/')
def my_form():
    return render_template('my-form.html')

@app.route('/', methods=['POST'])
def my_form_post():
    
    selection = request.form['Socialmedia']
    print('Selection',selection)
    
    processed_text = request.form['text']
    print('text',processed_text)
    fetch(request.form['text'])
    
    radio = request.form['radio']
    print('Radio',radio)
    
    return redirect(url_for("submit", a=selection, b=processed_text, c=radio))

@app.route('/submit/<a>/<b>/<c>')
def submit(a, b, c):
    print('here')
#     list_object = [a,b,c]
    input_dict={
    "socialmedia": a,
    "keyword": b,
    "fetchmode": c
}
    list_object = solr_dict['data']
    return render_template("User.html", list_to_send=list_object)


def fetch(text):
    print('The user text is',text)
    
if __name__=='__main__':
    app.run()
    
# @app.route('/')
# def index():
#     return render_template('my-form.html')

# @app.route('/submit', methods=['POST'])
# def submit():
#     return 'You entered: {}'.format(request.form['text'])


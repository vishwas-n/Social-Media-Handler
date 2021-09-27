from flask import Flask
from flask_restful import Api, Resource, reqparse
from twitter_connector import Twitter

app = Flask(__name__)
api = Api(app)

TWITTER = "twitter"
ONLINE = "online"

class SocialMedia(Resource):

    def __init__(self):
        self.twitter = Twitter()

    def get(self):
        print("Got GET request. Fetching Data")
        parser = reqparse.RequestParser()
        parser.add_argument('socialmedia', required=True)
        parser.add_argument('keyword', required=True)
        parser.add_argument('fetchmode', required=True)
        params = parser.parse_args()

        if str(params['fetchmode']).lower() == ONLINE.lower():
            data = self.get_live_data(params)
        else:
            data = self.get_offline_data(params)
        #if str(params['socialmedia']).lower() == TWITTER.lower():
            #data = self.twitter.get_tweets_for_keyword(str(params['keyword']))

        return {'data' : data}, 200

    def get_live_data(self, params):
        if str(params['socialmedia']).lower() == TWITTER.lower():
            data = self.twitter.get_tweets_for_keyword(str(params['keyword']))
            return data
        return []

    def get_offline_data(self, params):
        if str(params['socialmedia']).lower() == TWITTER.lower():
            data = self.twitter.get_tweets_offline(str(params['keyword']))
            return data
        return []


api.add_resource(SocialMedia, '/social_media_handle')

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 8990)

from flask import Flask, request, jsonify
from flask_restful import Api, Resource, reqparse
from solr_connector import Indexer, SearchHelper
from collections import OrderedDict
import requests
import argparse

app = Flask(__name__)
api = Api(app)

SUBSCRIBE = "subscribe"
UNSUBSCRIBE = "unsubscribe"
subscriber_map = OrderedDict()
subscriber_list = set()
topics_list_global = []


class Subscriber(Resource):

    # subscriber_map = OrderedDict()
    def __init__(self):
        self.indexer = Indexer()
        self.search_helper = SearchHelper()

    def post(self, action):

        print("Got POST request for subscriber.")
        parser = reqparse.RequestParser()
        parser.add_argument('topics', action='append', required=True)
        params = parser.parse_args()

        if str(action).lower() == SUBSCRIBE:
            return self.subscribe(params)
        elif str(action).lower() == UNSUBSCRIBE:
            return self.unsubscribe(params)

        return {"key": 'INVALID PATH'}, 400

    def subscribe(self, params):
        subscriber_id = request.remote_addr

        if subscriber_id not in subscriber_map:
            subscriber_map[subscriber_id] = set()

        topic_list = subscriber_map.get(subscriber_id)
        if type(params['topics']) == str:
            topic_list.add(params['topics'])
        elif type(params['topics']) == list:
            topic_list.update(params['topics'])

        solr_docs = []
        for item in subscriber_map.items():
            solr_doc = {
                "doc_type": "subscriber_data",
                "subscriber_id": item[0],
                "topics": list(item[1])
            }
            solr_docs.append(solr_doc)

        if len(solr_doc) > 0:
            self.indexer.delete_docs(q='doc_type:subscriber_data')
            self.indexer.create_documents(solr_docs)

        return {"key": 'success'}, 200

    def unsubscribe(self, params):
        subscriber_id = request.remote_addr

        topic_list = []
        if subscriber_id in subscriber_map:
            topic_list = subscriber_map.get(subscriber_id)

        if type(params['topics']) == str:
            if params['topics'] in topic_list:
                topic_list.remove(params['topics'])
        elif type(params['topics']) == list:
            for topic in params['topics']:
                if topic in topic_list:
                    topic_list.remove(topic)

        solr_docs = []
        for item in subscriber_map.items():
            if len(item[1]) > 1:
                solr_doc = {
                    "doc_type": "subscriber_data",
                    "subscriber_id": item[0],
                    "topics": list(item[1])
                }

                solr_docs.append(solr_doc)

        self.indexer.delete_docs(q='doc_type:subscriber_data')
        if len(solr_docs) > 0:
            self.indexer.create_documents(solr_docs)

        return {"key": 'success'}, 200


class Advertise(Resource):

    def __init__(self):
        self.indexer = Indexer()

    def post(self):
        print("Got POST request for Advertise.")
        parser = reqparse.RequestParser()
        parser.add_argument('topics', action='append', required=True)
        params = parser.parse_args()

        return self.advertise(params['topics'])

    def advertise(self, topics):

        payload = {
            "advertise_flag": "yes",
            "advertise_action": "advertise",
            "topics": topics,
            "data": {}
        }

        for topic in topics:
            if topic not in topics_list_global:
                topics_list_global.append(topic)

        solr_doc = {
            "doc_type": "topics_data",
            "topics": topics_list_global
        }

        if len(topics_list_global) > 0:
            self.indexer.delete_docs(q='doc_type:topics_data')
            self.indexer.create_documents([solr_doc])

        subscriber_ids = subscriber_map.keys()
        if len(subscriber_ids) == 0:
            subscriber_ids = subscriber_list

        for subscriber_id in subscriber_ids:
            list_object = requests.post(url='http://' + subscriber_id + ':8992/notify', json=payload)

        return {"key": "SUCCESS"}, 200


class Deadvertise(Resource):

    def __init__(self):
        self.indexer = Indexer()

    def post(self):
        print("Got POST request for Deadvertise.")
        parser = reqparse.RequestParser()
        parser.add_argument('topics', action='append', required=True)
        params = parser.parse_args()

        return self.deadvertise(params['topics'])

    def deadvertise(self, topics):
        payload = {
            "advertise_flag": "yes",
            "advertise_action": "deadvertise",
            "topics": topics,
            "data": {}
        }

        for topic in topics:
            topics_list_global.remove(topic)
            for item in subscriber_map.items():
                if topic in item[1]:
                    subscriber_map.get(item[0]).remove(topic)

        solr_docs = []
        for item in subscriber_map.items():
            if len(item[1]) > 1:
                solr_doc = {
                    "doc_type": "subscriber_data",
                    "subscriber_id": item[0],
                    "topics": list(item[1])
                }

                solr_docs.append(solr_doc)

        self.indexer.delete_docs(q='doc_type:subscriber_data')
        if len(solr_docs) > 0:
            self.indexer.create_documents(solr_docs)

        solr_doc = {
            "doc_type": "topics_data",
            "topics": topics_list_global
        }

        self.indexer.delete_docs(q='doc_type:topics_data')
        if len(topics_list_global) > 0:
            self.indexer.create_documents(solr_doc)

        subscriber_ids = subscriber_map.keys()
        if len(subscriber_ids) == 0:
            subscriber_ids = subscriber_list

        for subscriber_id in subscriber_ids:
            list_object = requests.post(url='http://' + subscriber_id + ':8992/notify', json=payload)

        return {"key": "SUCCESS"}, 200


class Register(Resource):

    def post(self):
        subscriber_id = request.remote_addr
        print("Got POST request for REGISTER for ", subscriber_id)

        if subscriber_id not in subscriber_list:
            subscriber_list.add(subscriber_id)

        payload = {
            "advertise_flag": "yes",
            "advertise_action": "advertise",
            "topics": topics_list_global,
            "data": {}
        }
        print("Register response: Sending topics to notify ", payload)
        response = requests.post(url='http://' + subscriber_id + ':8992/notify', json=payload)

        return {'topics': topics_list_global}, 200


class RecieveData(Resource):

    def __init__(self):
        self.indexer = Indexer()

    def post(self):
        print("Got POST request for Receive Data.")
        # parser = reqparse.RequestParser()
        # parser.add_argument("topic", required=True)
        # parser.add_argument("language", required=True)
        # parser.add_argument("data_list", action='append', required=True)
        # params = parser.parse_args()

        solr_docs_to_index = []
        print("Data list length obtained from publisher: ", len(request.json))
        for data_entry in request.json:
            solr_doc = {
                'doc_type': 'tweet_data',
                'topic': data_entry['topic'],
                'language': data_entry['language'],
                'data_list': data_entry['data_list']
            }
            solr_docs_to_index.append(solr_doc)

        self.indexer.create_documents(solr_docs_to_index)

        for subscriber_id in subscriber_map:
            payload = OrderedDict()
            topics = list(subscriber_map.get(subscriber_id))
            for solr_doc in solr_docs_to_index:
                if solr_doc['topic'] in topics:
                    if solr_doc['topic'] in payload:
                        tweet_list = payload.get(solr_doc['topic'])
                        tweet_list.extend(solr_doc['data_list'])
                    else:
                        payload[solr_doc['topic']] = solr_doc['data_list']

            actual_payload = {
                "advertise_flag": "no",
                "advertise_action": "",
                "topics": topics,
                "data": payload
            }

            print("HITTING subscriber url: ", 'http://' + subscriber_id + ':8992/notify')
            response = requests.post(url='http://' + subscriber_id + ':8992/notify', json=actual_payload)
        return {}, 200


class SubscriberData(Resource):

    def get(self):
        return_map = {}
        for item in subscriber_map.items():
            return_map[item[0]] = list(item[1])

        return {"topics_list": topics_list_global,
                "subscriptions": return_map}, 200


api.add_resource(Subscriber, '/subscriber/<action>')
api.add_resource(Advertise, '/advertise')
api.add_resource(Deadvertise, '/deadvertise')
api.add_resource(Register, '/register_subscriber')
api.add_resource(RecieveData, '/receive_data')
api.add_resource(SubscriberData, '/get_subscriptions')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--port", type=str, help="Port on which to start the app")
    argv = parser.parse_args()

    indexer = Indexer()
    solr_doc = {
        'doc_type': 'test',
        'topic': ["test"],
        'language': "en",
        'data_list': ["test a", "test b"],
        'subscriber_id': "test"
    }
    indexer.create_documents([solr_doc])
    indexer.delete_docs(q='doc_type:test')

    search_helper = SearchHelper()
    try:
        topics_list = search_helper.searchTopics()
        for topic in topics_list:
            if topic not in topics_list_global:
                topics_list_global.append(topic)

        subscriber_map_local = search_helper.searchWithFilter('doc_type:subscriber_data')
        for item in subscriber_map_local.items():
            subscriber_list.add(item[0])
            for topic in item[1]:
                if topic not in topics_list_global:
                    topics_list_global.extend(item[1])
        if len(subscriber_map_local.keys()) > 0:
            subscriber_map = subscriber_map_local

    except Exception as e:
        print("Cannot connect to SOLR")
        raise e

    app.run(host='0.0.0.0', port=argv.port)

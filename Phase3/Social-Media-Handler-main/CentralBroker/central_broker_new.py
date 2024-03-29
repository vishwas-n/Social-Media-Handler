from flask import Flask, request, jsonify
from flask_restful import Api, Resource, reqparse
from solr_connector import Indexer, SearchHelper
from collections import OrderedDict
import requests
import argparse
import socket

app = Flask(__name__)
api = Api(app)

SUBSCRIBE = "subscribe"
UNSUBSCRIBE = "unsubscribe"
subscriber_map = OrderedDict()
topic_to_subscriber_map = OrderedDict()
subscriber_list_global = set()
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

        subscriber_id = request.remote_addr
        if request.json is not None and 'subscriber_id' in request.json:
            subscriber_id = request.json['subscriber_id']

        brokers_handled_in_request = []
        if request.json is not None and 'handler_broker' in request.json:
            brokers_handled_in_request = request.json['handler_broker']

        if str(action).lower() == SUBSCRIBE:
            return self.subscribe(params, subscriber_id, brokers_handled_in_request)
        elif str(action).lower() == UNSUBSCRIBE:
            return self.unsubscribe(params, subscriber_id, brokers_handled_in_request)

        return {"key":'INVALID PATH'}, 400

    def subscribe(self, params, subscriber_id, brokers_handled_in_request):

        # subscriber_id = request.remote_addr
        # if 'subscriber_id' in request.json:
        #     subscriber_id = request.json['subscriber_id']

        hostname = socket.gethostname()
        broker_id = socket.gethostbyname(hostname)

        topics_to_subscribe = params['topics']
        topics_to_forward = []
        for topic in topics_to_subscribe:
            if topic not in topics_list_global:
                topics_to_forward.append(topic)
        #for topics in topics_to_forward:
        #    topics_to_subscribe.remove(topic)

        if len(topics_to_subscribe) > len(topics_to_forward):
            if subscriber_id not in subscriber_map:
                subscriber_map[subscriber_id] = set()

            topic_list = subscriber_map.get(subscriber_id)
            topic_list.update(topics_to_subscribe)

            solr_docs = []
            for item in subscriber_map.items():
                solr_doc = {
                    "doc_type": "subscriber_data",
                    "handler_broker": broker_id,
                    "subscriber_id" : item[0],
                    "topics" : list(item[1])
                }
                solr_docs.append(solr_doc)

            if len(solr_docs) > 0:
                self.indexer.delete_docs(q='doc_type:subscriber_data AND handler_broker:'+broker_id)
                self.indexer.create_documents(solr_docs)

        if len(topics_to_forward) > 0:

            response = requests.get(url='http://rendezvous_node:8989/get_neighbour_brokers')
            brokers_list = response.json()['brokers']
            payload_brokers_list = list().extend(brokers_list)
            payload_brokers_list.extend(brokers_handled_in_request)
            payload = {
                'handler_broker' : payload_brokers_list.append(broker_id),
                "subscriber_id": subscriber_id,
                "topics": topics_to_forward
            }
            for broker in brokers_list:
                # requests.post(url='http://localhost:8990/subscriber/subscribe', json=payload)
                if broker not in brokers_handled_in_request:
                    print('Forwarding subscribe request to:', broker)
                    requests.post(url='http://' + broker + ':8990/subscriber/subscribe', json=payload)

        return {"key":'success'}, 200

    def unsubscribe(self, params, subscriber_id, brokers_handled_in_request):

        # subscriber_id = request.remote_addr
        # if 'subscriber_id' in request.json:
        #     subscriber_id = request.json['subscriber_id']

        hostname = socket.gethostname()
        broker_id = socket.gethostbyname(hostname)

        topics_to_unsubscribe = params['topics']
        topics_to_forward = []
        for topic in topics_to_unsubscribe:
            if topic not in topics_list_global:
                topics_to_forward.append(topic)
        for topics in topics_to_forward:
            topics_to_unsubscribe.remove(topic)

        topic_list = []
        if subscriber_id in subscriber_map:
            topic_list = subscriber_map.get(subscriber_id)

        updated_flag = False
        for topic in topics_to_unsubscribe:
            if topic in topic_list:
                topic_list.remove(topic)
                updated_flag = True

        if updated_flag:
            solr_docs = []
            for item in subscriber_map.items():
                if len(item[1]) > 0:
                    solr_doc = {
                        "doc_type": "subscriber_data",
                        "handler_broker": broker_id,
                        "subscriber_id" : item[0],
                        "topics" : list(item[1])
                    }

                    solr_docs.append(solr_doc)

            self.indexer.delete_docs(q='doc_type:subscriber_data AND handler_broker:'+broker_id)
            if len(solr_docs) > 0:
                self.indexer.create_documents(solr_docs)

        if len(topics_to_forward) > 0:
            response = requests.get(url='http://rendezvous_node:8989/get_neighbour_brokers')
            brokers_list = response.json()['brokers']
            payload_brokers_list = list().extend(brokers_list)
            payload_brokers_list.extend(brokers_handled_in_request)
            payload = {
                'handler_broker': payload_brokers_list.append(broker_id),
                "subscriber_id": subscriber_id,
                "topics": topics_to_forward
            }
            for broker in brokers_list:
                # requests.post(url='http://localhost:8990/subscriber/unsubscribe', json=payload)
                if broker not in brokers_handled_in_request:
                    print('Forwarding unsubscribe request to:', broker)
                    requests.post(url='http://' + broker + ':8990/subscriber/unsubscribe', json=payload)

        return {"key":'success'}, 200

class Advertise(Resource):

    def __init__(self):
        self.indexer = Indexer()

    def post(self):
        print("Got POST request for Advertise.")
        # parser = reqparse.RequestParser()
        # parser.add_argument('topics', action='append', required=True)
        # params = parser.parse_args()
        advertise_forward = False
        if request.json is not None and "advertise_forward" in request.json:
            if str(request.json["advertise_forward"]).lower() == "yes":
                advertise_forward = True
        return self.advertise(request.json['topics'], advertise_forward)

    def advertise(self, topics, advertise_forward):

        hostname = socket.gethostname()
        broker_id = socket.gethostbyname(hostname)

        if not advertise_forward:
            print("Updating Topics list")
            for topic in topics:
                if topic not in topics_list_global:
                    topics_list_global.append(topic)

            solr_doc = {
                "doc_type": "topics_data",
                "handler_broker": broker_id,
                "topics": topics_list_global
            }

            if len(topics_list_global) > 0:
                self.indexer.delete_docs(q='doc_type:topics_data AND handler_broker:'+broker_id)
                self.indexer.create_documents([solr_doc])

            requests.post(url='http://rendezvous_node:8989/register_topic', json={"topics": topics})

        subscribers_to_notify = []
        for subscriber_id in subscriber_list_global:
            subscribers_to_notify.append(subscriber_id)

        subscribers_already_handled = []
        if 'subscribers_already_handled' in request.json:
            subscribers_already_handled = request.json['subscribers_already_handled']
            for subscriber_id in subscribers_already_handled:
                subscribers_to_notify.remove(subscriber_id)

        subscribers_already_handled.extend(subscribers_to_notify)

        if 'handler_broker' not in request.json:

            payload = {
                "handler_broker": [broker_id],
                "subscribers_already_handled": subscribers_already_handled,
                "advertise_flag": "yes",
                "advertise_forward": "yes",
                "advertise_action": "advertise",
                "topics": topics,
                "data": {}
            }
            for subscriber_id in subscribers_to_notify:
                requests.post(url='http://'+subscriber_id+':8992/notify', json=payload)

            response = requests.get(url='http://rendezvous_node:8989/get_neighbour_brokers')
            brokers_list = response.json()['brokers']
            for broker in brokers_list:
                print("Forwarding Advertise to broker:", broker)
                requests.post(url='http://' + broker + ':8992/advertise', json=payload)
        else:
            response = requests.get(url='http://rendezvous_node:8989/get_neighbour_brokers')
            brokers_list = response.json()['brokers']
            visited_brokers = request.json['handler_broker']
            visited_brokers.append(broker_id)
            payload = {
                "handler_broker": visited_brokers,
                "subscribers_already_handled": subscribers_already_handled,
                "advertise_flag": "yes",
                "advertise_forward": "yes",
                "advertise_action": "advertise",
                "topics": topics,
                "data": {}
            }
            for subscriber_id in subscribers_to_notify:
                requests.post(url='http://' + subscriber_id + ':8992/notify', json=payload)

            for broker in brokers_list:
                if broker not in visited_brokers:
                    print("Forwarding Advertise to broker:", broker)
                    requests.post(url='http://' + broker + ':8992/advertise', json=payload)


        return {"key": "SUCCESS"}, 200

class Deadvertise(Resource):

    def __init__(self):
        self.indexer = Indexer()

    def post(self):
        print("Got POST request for Deadvertise.")
        # parser = reqparse.RequestParser()
        # parser.add_argument('topics', action='append', required=True)
        # params = parser.parse_args()
        deadvertise_forward = False
        if request.json is not None and "advertise_forward" in request.json:
            if str(request.json["advertise_forward"]).lower() == "yes":
                deadvertise_forward = True
        return self.deadvertise(request.json['topics'], deadvertise_forward)

    def deadvertise(self, topics, deadvertise_forward):

        hostname = socket.gethostname()
        broker_id = socket.gethostbyname(hostname)

        if not deadvertise_forward:

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
                        "handler_broker": broker_id,
                        "subscriber_id": item[0],
                        "topics": list(item[1])
                    }

                    solr_docs.append(solr_doc)

            self.indexer.delete_docs(q='doc_type:subscriber_data AND handler_broker:'+broker_id)
            if len(solr_docs) > 0:
                self.indexer.create_documents(solr_docs)

            solr_doc = {
                "doc_type": "topics_data",
                "handler_broker": broker_id,
                "topics": topics_list_global
            }

            self.indexer.delete_docs(q='doc_type:topics_data AND handler_broker:'+broker_id)
            if len(topics_list_global) > 0:
                self.indexer.create_documents(solr_doc)

            requests.post(url='http://rendezvous_node:8989/deregister_topic', json={"topics": topics})

        subscribers_to_notify = []
        for subscriber_id in subscriber_list_global:
            subscribers_to_notify.append(subscriber_id)

        subscribers_already_handled = []
        if 'subscribers_already_handled' in request.json:
            subscribers_already_handled = request.json['subscribers_already_handled']
        for subscriber_id in subscribers_already_handled:
            subscribers_to_notify.remove(subscriber_id)

        subscribers_already_handled.extend(subscribers_to_notify)

        if 'handler_broker' not in request.json:
            payload = {
                "handler_broker": [broker_id],
                "subscribers_already_handled": subscribers_already_handled,
                "advertise_flag": "yes",
                "advertise_forward": "yes",
                "advertise_action": "deadvertise",
                "topics": topics,
                "data": {}
            }
            for subscriber_id in subscribers_to_notify:
                requests.post(url='http://' + subscriber_id + ':8992/notify', json=payload)

            response = requests.get(url='http://rendezvous_node:8989/get_neighbour_brokers')
            brokers_list = response.json()['brokers']
            for broker in brokers_list:
                requests.post(url='http://' + broker + ':8992/deadvertise', json=payload)
        else:
            response = requests.get(url='http://rendezvous_node:8989/get_neighbour_brokers')
            brokers_list = response.json()['brokers']
            visited_brokers = request.json['handler_broker']
            visited_brokers.append(broker_id)
            payload = {
                "handler_broker": visited_brokers,
                "subscribers_already_handled": subscribers_already_handled,
                "advertise_flag": "yes",
                "advertise_forward": "yes",
                "advertise_action": "deadvertise",
                "topics": topics,
                "data": {}
            }
            for subscriber_id in subscribers_to_notify:
                requests.post(url='http://' + subscriber_id + ':8992/notify', json=payload)

            for broker in brokers_list:
                if broker not in visited_brokers:
                    requests.post(url='http://' + broker + ':8992/deadvertise', json=payload)

        return {"key": "SUCCESS"}, 200

class Register(Resource):

    def post(self):
        subscriber_id = request.remote_addr
        print("Got POST request for REGISTER for ", subscriber_id)

        if subscriber_id not in subscriber_list_global:
            subscriber_list_global.add(subscriber_id)

        response = requests.get(url='http://rendezvous_node:8989/get_all_topics')
        return_topics_list = response.json()["topics"]

        payload = {
            "advertise_flag": "yes",
            "advertise_action": "advertise",
            "topics": return_topics_list,
            "data": {}
        }
        print("Register response: Sending topics to notify ", payload)
        response = requests.post(url='http://' + subscriber_id + ':8992/notify', json=payload)

        return {'topics': return_topics_list}, 200


class ReceiveData(Resource):

    def __init__(self):
        self.indexer = Indexer()

    def post(self):
        print("Got POST request for Receive Data.")
        # parser = reqparse.RequestParser()
        # parser.add_argument("topic", required=True)
        # parser.add_argument("language", required=True)
        # parser.add_argument("data_list", action='append', required=True)
        # params = parser.parse_args()

        hostname = socket.gethostname()
        broker_id = socket.gethostbyname(hostname)

        solr_docs_to_index = []
        print("Data list length obtained from publisher: ", len(request.json))
        for data_entry in request.json:
            solr_doc = {
                'doc_type': 'tweet_data',
                'data_source': 'twitter',
                'handler_broker': broker_id,
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
                "handler_broker": [broker_id],
                "advertise_flag": "no",
                "advertise_action": "",
                'handler_broker': broker_id,
                "topics": topics,
                "data": payload
            }

            print("HITTING subscriber url: ", 'http://'+subscriber_id+':8992/notify')
            response = requests.post(url='http://'+subscriber_id+':8992/notify', json=actual_payload)

        return {}, 200

class SubscriberData(Resource):

    def get(self):
        return_map = {}
        for item in subscriber_map.items():
            return_map[item[0]] = list(item[1])

        return {"topics_list_at_broker": topics_list_global,
                "subscriptions_at_broker": return_map}, 200



api.add_resource(Advertise, '/advertise')
api.add_resource(Deadvertise, '/deadvertise')
api.add_resource(Register, '/register_subscriber')
api.add_resource(Subscriber, '/subscriber/<action>')
api.add_resource(ReceiveData, '/receive_data')
api.add_resource(SubscriberData, '/get_subscriptions')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--port", type=str, help="Port on which to start the app")
    parser.add_argument("--brokers", nargs='*', type=str, help="List of neighbouring brokers")
    argv = parser.parse_args()

    indexer = Indexer()
    solr_doc = {
        'doc_type': 'test',
        'handler_broker': 'test',
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
            subscriber_list_global.add(item[0])
            for topic in item[1]:
                if topic not in topics_list_global:
                    topics_list_global.extend(item[1])
        if len(subscriber_map_local.keys()) > 0:
            subscriber_map = subscriber_map_local

    except Exception as e:
        print("Cannot connect to SOLR")
        raise e

    requests.post(url='http://rendezvous_node:8989/register_broker', json={"topics":topics_list_global})
    app.run(host = '0.0.0.0', port = argv.port)
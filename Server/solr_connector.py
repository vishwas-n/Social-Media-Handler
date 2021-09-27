import pysolr
import requests

CORE_NAME = "base_core"
#IP = "localhost"
IP = "solr"
#IP = "3.16.37.251"


class Indexer:
    def __init__(self):
        self.solr_url = f'http://{IP}:8983/solr/'
        self.connection = pysolr.Solr(self.solr_url + CORE_NAME, always_commit=True, timeout=5000000)

    def create_documents(self, docs):
        print("Indexing ", len(docs), str(" documents into solr at IP: {IP} and core :{core}").format(IP=IP, core=CORE_NAME))
        print(self.connection.add(docs))

    def add_fields(self):
        data = {
            "add-field": [
                {
                    "name": "data_text",
                    "type": "string",
                    "multiValued": False
                }
            ]
        }

        print(requests.post(self.solr_url + CORE_NAME + "/schema", json=data).json())



class SearchHelper:

    def __init__(self):
        self.solr_url = f'http://{IP}:8983/solr/'
        self.connection = pysolr.Solr(self.solr_url + CORE_NAME, always_commit=True, timeout=5000000)

    def search(self, keyword):
        solrDocs = self.connection.search(q="*:*", **{'fq': 'keyword:' + keyword}, rows=25)
        tweet_list = []
        for doc in solrDocs.docs:
            tweet_list.append(doc['data_text'][0])
        if len(tweet_list) == 0:
            tweet_list = ['No Data Found']
        return tweet_list


import tweepy
from solr_connector import Indexer
from solr_connector import SearchHelper

class Twitter:
    def __init__(self):
        self.auth = tweepy.OAuthHandler("9CIRioClI3LE9TqyzYFnpF2Y5", "GwxZieFYqK7bxUcbAQLYCqfvLvhY4T5dNakKo1m2PwXzreMN6P")
        self.auth.set_access_token("743685942515404805-9mwQVL9FKNG3Y6FZGaaQPjuTLQdzpV9", "NjiE4BpjfwylVRDEIzPJoxftla7m0EjScJ0izEdFVjkf8")
        self.api = tweepy.API(self.auth, wait_on_rate_limit=True)
        self.solr_indexer = Indexer()
        self.solr_search_helper = SearchHelper()

    def get_tweets_offline(self, keyword):
        return self.solr_search_helper.search(keyword=keyword)

    def get_tweets_for_keyword(self, keyword):
        print("Fetching tweets by Keyword: {keyword}".format(keyword=keyword))
        tweets_list = []
        solr_documents_to_index = []

        query = keyword + ' ' + '-filter:retweets'
        for data in tweepy.Cursor(self.api.search_tweets, q=query, count=25, tweet_mode="extended", lang="en", include_entities=True).pages(1):
            print("Fetching {count} tweets".format(count=25))
            for tweet in data:
                tweets_list.append(tweet.full_text)
                solr_documents_to_index.append(self.get_solr_doc_from_tweet(tweet, keyword))

        print("Preparing indexing docs")
        self.solr_indexer.create_documents(solr_documents_to_index)
        return tweets_list

    def get_solr_doc_from_tweet(self, tweet, keyword):
        data_text = tweet.full_text
        user_name = tweet.author.screen_name

        doc = {
            'user_name': user_name,
            'data_text': data_text,
            'keyword': keyword
        }

        return doc

# if __name__ == "__main__":
#     twitter = Twitter()
#     twitter.get_tweets_for_keyword('covid')



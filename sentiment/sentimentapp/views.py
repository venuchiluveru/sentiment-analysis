from django.shortcuts import render
import tweepy
import nltk
from nltk.corpus import stopwords, state_union
from nltk.sentiment import SentimentIntensityAnalyzer
import re
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree
from django.conf import settings
from django.http import JsonResponse

# Create your views here.
ckey = settings.CKEY
csecret = settings.CSECRET
atoken = settings.ATOKEN
asecret = settings.ASECRET
auth = tweepy.OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)
api = tweepy.API(auth)

def clean_tweet(text):
    text = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", text).split())
    return text

def preprocess(text):
    text = nltk.word_tokenize(text)
    text = nltk.pos_tag(text)
    return text

def entity_extraction(text):
    val = ''
    label_name = 'None'
    chunked = ne_chunk(pos_tag(word_tokenize(text)))
    continuous_chunk = []
    current_chunk = []
    for i in chunked:
        # if hasattr(i, 'label'):
        # 	print(i.label(), "=====label")
        if type(i) == Tree:
            current_chunk.append(" ".join([token for token, pos in i.leaves()]))
        if current_chunk:
            named_entity = " ".join(current_chunk)
            if named_entity not in continuous_chunk:
                continuous_chunk.append(named_entity)
                current_chunk = []
        else:
            continue
    return continuous_chunk

def calulate_sentiment(sentiment_analysis, data):
    val = []
    for value in data:
        tweet_data = {}
        if hasattr(value, 'full_text'):
            text = value.full_text
        else:
            text = value.text
        processed_text = clean_tweet(text)
        sentiment_scores = sentiment_analysis.polarity_scores(processed_text)
        tweet_data['text'] = text
        tweet_data['id'] = value.id
        if sentiment_scores['compound'] >= 0.05:
            tweet_data['sentiment'] = 'Positive'

        elif sentiment_scores['compound'] <= - 0.05:
            tweet_data['sentiment'] = 'Negative'

        else:
            tweet_data['sentiment'] = 'Neutral'

        tweet_data['entity'] = entity_extraction(processed_text)
        val.append(tweet_data)
    # print(val)
    return val


def tweet_list(request):
    result = []
    if request.method == "GET":
        sentiment_analysis = SentimentIntensityAnalyzer()
        data = api.user_timeline(screen_name='elonmusk', count=100, include_rts=False, tweet_mode='extended')
        result = calulate_sentiment(sentiment_analysis, data)
    return render(request, 'sentimentapp/tweet_list.html', {'tweets': result})

def tweet_search(request):
    search_words = request.GET['search_text']
    sentiment_analysis = SentimentIntensityAnalyzer()
    result = []
    if request.method == "GET":
        new_search = search_words + " -filter:retweets"
        tweets = tweepy.Cursor(api.search,
                           q=new_search,
                           lang="en").items(100)

        print(tweets)
        result = calulate_sentiment(sentiment_analysis, tweets)
    return JsonResponse({'tweets': result})
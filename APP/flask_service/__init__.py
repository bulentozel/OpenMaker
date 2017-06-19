from flask import Flask
from flask_httpauth import HTTPBasicAuth
from LibOM.Tools import *

# Setting up connection to the Media Watch Tower:
print "Connecting to WatchTower"
ClientWT = WatchTower()

# Setting up connection to the Media Watch Tower:
print "Connecting to Twitter"
ClientTwitter = Twitter()

# Loading the maker dictionary:
MD = MakerDictionary()

# Retrieving influencer lists:
influencer_names = ClientWT.retrieve_influencers()
print "Number of influencers from the WatchTower: ", len(influencer_names)


# Collecting tweets of the influencers:
debates = ClientTwitter.retrieve_tweets(influencer_names, 200)

# Populating the score board:
print "The user data retrieved from Twitter: "
SB = ScoreBoard()
for inf in debates.keys():
    ntweets = debates[inf]['ntweets']
    text = debates[inf]['content']
    nmappings, nwords, counts = extract_features(text, MD)
    features = {"ntweets":ntweets, "nwords":nwords, "nmappings":nmappings, "counts":counts}
    SB.post_scores(inf, features)
    print inf, ntweets, nmappings, nwords
 
# Initialization of app and auhentication:
app = Flask(__name__, static_url_path="")
auth = HTTPBasicAuth()

import flask_service.api


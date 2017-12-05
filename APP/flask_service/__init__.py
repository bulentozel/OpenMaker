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
WTInfluencers = ClientWT.retrieve_influencers()
print "Number of influencers from the WatchTower: ", len(WTInfluencers)

# Collecting tweets of the influencers:
debates = ClientTwitter.retrieve_tweets(WTInfluencers, 200)
#debates = ClientTwitter.retrieve_tweets(WTInfluencers[0:10], 10)
#debates = ClientTwitter.retrieve_tweets(WTInfluencers, 50)



# Loading previous scoreboard:
SB = ScoreBoard()
try:
    SB.import_board("./data/scoreboard.p")
except IOError:
    print "No previously stored Scoreboard is found."


# Populating the score board:
print"The user data retrieved from Twitter: "  
for inf in debates.keys():
    ntweets = debates[inf]['ntweets']
    if not ntweets: continue
    text = debates[inf]['content']
    nmappings, nwords, counts = extract_features(text, MD)
    features = {"source":0,"ntweets":ntweets, "nwords":nwords, "nmappings":nmappings, "counts":counts}
    SB.post_scores(inf, features)
    print inf, ntweets, nmappings, nwords


# Store the baord:
SB.store_the_board("./data/scoreboard.p")

# Initialization of app and auhentication:
app = Flask(__name__, static_url_path="")
auth = HTTPBasicAuth()

import flask_service.api


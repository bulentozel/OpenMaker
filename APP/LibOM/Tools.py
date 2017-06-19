"""This module contains a set of functions and classes to be used while analyzing themes/memes within maker community.

Attributes:
    *
Classes:
    * WatchTower: Connects to BOUNs Media Watch Tower API to retrieve influencers and themes.
    * Twitter: Connects to Twitter API to harvest tweets of the predetermined user(s)
    * MakerDictionary: The class has a set of tools (methods) and attributes that is used to to load and compile 
     regular expressions/patterns for maker related keywords and phrases.
    * ScoreBoard: The class has a set of tools to compute, normalize and rank content of tweets/texts of an actor or a group of actors/

Functions:
    * extract_features:  It extracts maker related features using other objects in the library.
Todo:
    * Adding Python Docstrings
    * 
"""

import requests, oauth2, json
import pickle, csv
import re

class WatchTower:

    url_api = 'http://138.68.92.181:8484/api'
    path_themes = '/get_themes'
    path_influencers = '/get_influencers'

    def __init__(self, influencers=None):
        self.influencers = influencers

    def retrieve_influencers(self):
        resp = requests.get(WatchTower.url_api + WatchTower.path_themes)
        if resp.status_code != 200: return None
        self.influencers = list()
        for theme in resp.json()['themes']:
            tname = theme['name']
            rurl = WatchTower.url_api + WatchTower.path_influencers + '/' + tname
            resp = requests.get(rurl)
            influencers = resp.json()['influencers']
            for influencer in influencers:
                name = influencer['username']
                if name in self.path_influencers: continue
                self.influencers.append(name)
        return self.influencers


class Twitter:

    Consumer_Key = ""  # API key
    Consumer_Secret = ""  # API secret

    Access_Token = ""
    Access_Token_Secret = ""

    url_api = "https://api.twitter.com/1.1/statuses/user_timeline.json?tweet_mode=extended"

    def __init__(self, new=None):
        if new:
            self.consumer = oauth2.Consumer(key=new['Consumer_Key'], secret=new['Consumer_Secret'])
            self.access_token = oauth2.Token(key=new['Access_Token'], secret=new['Access_Token_Secret'])
            self.Client = oauth2.Client(self.consumer, self.access_token)
        else:
            self.consumer = oauth2.Consumer(key=Twitter.Consumer_Key, secret=Twitter.Consumer_Secret)
            self.access_token = oauth2.Token(key=Twitter.Access_Token, secret=Twitter.Access_Token_Secret)
            self.Client = oauth2.Client(self.consumer, self.access_token)

    def accumulate_auser_tweets(self, auser, nlatest = 200):
        # type: (str, int) -> dict
        request = Twitter.url_api + "&screen_name="+ auser + "&count=" + str(nlatest)
        response, data = self.Client.request(request)
        tweets = json.loads(data)
        if isinstance(tweets, dict):
            message = "Error at Connection to Twitter API: {1}".format(tweets['errors'])
            print "Connection errot to the account ", auser
            raise Exception(message)
        content = ""
        ntweet = 0
        for tweet in tweets:
            if tweet["lang"] != "en": continue
            ntweet += 1
            content += tweet["full_text"] + '\n'
        user_content = {"ntweets": ntweet, "content": content}
        return user_content

    def retrieve_tweets(self, userlist, nlatest=200):
        tweets = dict()
        userlist = [str(x) for x in userlist if isinstance(x, basestring)]
        for user in userlist:
            try:
                tweets[user] = self.accumulate_auser_tweets(user,nlatest)
            except Exception:
                tweets[user] = {"ntweets": 0, "content": ""}
        return tweets


class MakerDictionary:
    csv_terms = "./data/MakerDict.csv"
    csv_categories = "./data/MakerCat.csv"
    
    @staticmethod
    def load_mapped_terms(csv_terms, csv_categories):
        table_Mmappings = dict()
        with open(csv_terms, mode='r') as infile:
            reader = csv.reader(infile)
            for row in reader:
                entry = row[0]
                categories = row[1:]
                categories = [cat for cat in categories if cat]
                table_Mmappings[entry] = categories
        pickle.dump(table_Mmappings, open("./data/table_Mmappings.p", "wb"))

        # Loading features to words table:
        table_Mfeatures = dict()
        try:
            table_Mfeatures = pickle.load(open("./data/table_Mfeatures.p", "rb"))
        except IOError:
            table_Mfeatures = {}
            with open(csv_categories, mode='r') as infile:
                reader = csv.reader(infile)
                category_names = reader.next()
                category_names = [cat.lower() for cat in category_names]
                category_codes = reader.next()
                for i, cat in enumerate(category_codes):
                    table_Mfeatures[cat] = {'name':category_names[i], 'content':list()}
            for entry in table_Mmappings.keys():
                for cat in table_Mmappings[entry]:
                    table_Mfeatures[cat]['content'].append(entry)
        pickle.dump(table_Mfeatures, open("./data/table_Mfeatures.p", "wb"))

        # compiling patterns::

        def form_word_pattern(key, isolate=True):
            if key[-1] == "*":
                thepattern = key[0:-1]
                thepattern += "[a-z']" + "*"
            else:
                thepattern = key
            thepattern = thepattern.replace("(", "\(")
            thepattern = thepattern.replace(")", "\)")
            if isolate: thepattern += "[.,;:]*"
            return thepattern

        def form_phrase_pattern(words):
            thepattern = ''
            for word in words:
                if thepattern:
                    thepattern += '\s+' + form_word_pattern(word, isolate=False)
                else:
                    thepattern += form_word_pattern(word, isolate=False)
            thepattern += "[.,;:]*"
            return thepattern

        table_patterns_keywords = dict()
        table_patterns_phrases = dict()
        for key, value in table_Mmappings.items():
            words = key.split()
            isphrase = False
            print words
            if len(words) > 1:
                thepattern = form_phrase_pattern(words)
                isphrase = True
            else:
                thepattern = form_word_pattern(key)

            p = re.compile(thepattern, re.IGNORECASE)
            if isphrase:
                table_patterns_phrases[p] = {"key": key, "categories": value}
            else:
                table_patterns_keywords[p] = {"key": key, "categories": value}
        pickle.dump(table_patterns_keywords, open("./data/patterns_words.p", "wb"))
        pickle.dump(table_patterns_phrases, open("./data/patterns_phrases.p", "wb"))
        return table_patterns_keywords, table_patterns_phrases, table_Mfeatures, table_Mmappings

    def __init__(self):

        self.categories = dict()
        with open(MakerDictionary.csv_categories, mode='r') as infile:
            reader = csv.reader(infile)
            category_names = reader.next()
            category_names = [cat.lower() for cat in category_names]
            category_codes = reader.next()
            self.categories = {category_names[i]:cat for i, cat in enumerate(category_codes)}
        self._load_patterns()
        

    def update_patterns(self,csv_terms=None,csv_categories=None):

        fterms = csv_terms if csv_terms else MakerDictionary.csv_terms
        fcats =  csv_categories if csv_categories else MakerDictionary.csv_categories

        compiled = MakerDictionary.load_mapped_terms(fterms, fcats)
        self.pattern_words = compiled[0]
        self.pattern_phrases = compiled[1]
        self.table_Mfeatures = compiled[2]
        self.table_Mmappings = compiled[3]

    def match_words(self, text):
        # type: str -> dict
        table_counts = dict()
        for key in self.table_Mfeatures: table_counts[key] = 0
        mapping_count = 0
        word_count = 0

        matched_list = list()
        not_matched_list = list()

        for line in text.split('\n'):
            words = line.strip().split()
            words = [word.strip() for word in words if word]
            for word in words:
                word_count += 1
                matched = 0
                for p in self.pattern_words.keys():
                    m = p.match(word)
                    if not m: continue
                    # print word
                    for cat in self.pattern_words[p]["categories"]:
                        matched += 1
                        table_counts[cat] += 1
                mapping_count += matched
                matched_list.append(word) if matched else not_matched_list.append(word)

        results = dict()
        results["nmappings"] = mapping_count
        results["counts"] = table_counts
        results["nwords"] = word_count
        results["matched"] = matched_list
        results["not_matched"] = not_matched_list
        return results

    def match_phrases(self, text):
        # type: str -> dict
        table_counts = dict()
        for key in self.table_Mfeatures: table_counts[key] = 0
        mapping_count = 0

        for line in text.split('\n'):
            for p in self.pattern_phrases.keys():
                m = p.findall(line)
                nfind = len(m)
                if not nfind: continue
                matched = 0
                # print m
                for cat in self.pattern_phrases[p]["categories"]:
                    matched += nfind
                    table_counts[cat] += nfind
                mapping_count += matched

        results = dict()
        results["nmappings"] = mapping_count
        results["counts"] = table_counts
        return results

    def get_category_name(self, code):
        cat = self.categories.keys()[self.categories.values().index(code)]
        return cat

    def _load_patterns(self):
        try:
            self.table_Mmappings = pickle.load(open("./data/table_Mmappings.p", "rb"))
            self.table_Mfeatures = pickle.load(open("./data/table_Mfeatures.p", "rb"))
            self.pattern_words = pickle.load(open("./data/patterns_words.p", "rb"))
            self.pattern_phrases = pickle.load(open("./data/patterns_phrases.p", "rb"))
        except IOError:
            fterms = MakerDictionary.csv_terms
            fcats = MakerDictionary.csv_categories
            compiled = MakerDictionary.load_mapped_terms(fterms, fcats)
            self.pattern_words = compiled[0]
            self.pattern_phrases = compiled[1]
            self.table_Mfeatures = compiled[2]
            self.table_Mmappings = compiled[3]


class ScoreBoard:

    @staticmethod
    def compute_scores(features):
        ntweets = features['ntweets']
        nwords = features['nwords']
        nmappings = features['nmappings']
        counts = features['counts']

        def transform(count, ntweets, nwords):
            count = float(count)
            per_tweet = count / ntweets if ntweets else 0
            per_word = count / nwords if nwords else 0
            return {'raw': count, 'per_tweet': per_tweet, 'per_word': per_word}

        overall = transform(nmappings, ntweets, nwords)
        scores = {key: transform(counts[key], ntweets, nwords) for key in counts.keys() if counts[key]}
        scores.update({"all": overall})
        return scores

    def __init__(self):
        self.table = dict()
        self.rankings = dict()
        
    def add_actor(self, actor, features):
        self.post_scores(actor, features)
        self.update_rankings()
    
    def remove_all(self):
        self.table = dict()
        self.rankings = dict()

    def remove_one(self, actor):
        del self.table[actor]
        self.update_rankings()

    def compute_rankings(self, category='all', stype = "per_tweet"):
        rankings = {a:self.table[a]['scores'][category][stype]
                       for a in self.table.keys()
                       if category in self.table[a]['scores'].keys()}
        rankings = sorted(rankings.items(), key=lambda x: x[1], reverse=True)
        self.rankings[(category,stype)] = rankings

    def get_rankings_one(self, category='all', stype='per_tweet'):
        key = (category,stype)
        if not key in self.rankings.keys():
            self.compute_rankings(category,stype)
        rankings = [x for x in self.rankings[key] if x[1] > 0]
        return rankings

    def get_score_one(self, actor, category='all', stype='per_tweet'):
        if not actor in self.table.keys(): return
        if not category in self.table[actor]['scores'].keys(): return
        return self.table[actor]['scores'][category][stype]

    def get_scores(self, actor, categories, stype='per_tweet'):
        scores = dict()
        for cat in categories:
            scores[cat] = self.get_score_one(actor,cat,stype)
        scores = {k:v for k,v in scores.items() if v}
        return scores
                   
    def is_on_board(self,actor):
        return actor in self.table.keys()

    def update_rankings(self):
        for key in self.rankings.keys():
            category = key[0]
            stype = key[1]
            self.compute_rankings(category,stype)

    def post_scores(self, actor, features):
        self.table[actor] = {
            'ntweets': features['ntweets'],
            'nwords': features['nwords'],
            'nmappings': features['nmappings'],
            'scores': ScoreBoard.compute_scores(features)}


def extract_features(text, MDict):
    matchings_phrases = MDict.match_phrases(text)
    nmappings = matchings_phrases['nmappings']
    matchings_words = MDict.match_words(text)
    nmappings += matchings_words['nmappings']
    nwords = matchings_words['nwords']
    counts = dict()
    for key in matchings_words['counts'].keys():
        counts[key] = matchings_words['counts'][key] + matchings_phrases['counts'][key]
    return nmappings, nwords, counts



if __name__ == '__main__':
    Client_WT = WatchTower()
    Client_Twitter = Twitter()
 
    influencer_names = Client_WT.retrieve_influencers()
    debates = Client_Twitter.retrieve_tweets(influencer_names[0:5], 5)

    SB = ScoreBoard()
    MD = MakerDictionary()
    for inf in debates.keys():
        ntweets = debates[inf]['ntweets']
        text = debates[inf]['content']
        nmappings, nwords, counts = extract_features(text, MD)
        features = {"ntweets":ntweets, "nwords":nwords, "nmappings":nmappings, "counts":counts}
        SB.add_actor(inf, features)

    
    for k, v in SB.table.items():
        print "_" * 20
        print k, v["ntweets"], v["nwords"], v["nmappings"]
        for type in v['scores'].keys():
            print type, v['scores'][type]
    

    print "_" * 100
    print "_" * 100


    SB.compute_rankings('0', 'per_word')
    SB.compute_rankings('5', 'per_word')
    SB.compute_rankings('all', 'per_word')

    print "_" * 60

    for k, v in SB.rankings.items(): print k, v

    print SB.get_rankings_one('all', 'per_word')
    print SB.get_rankings_one('1', 'raw')
    print SB.get_rankings_one('7', 'per_tweet')

    print "_" * 60
    for k, v in SB.rankings.items(): print k, v

    print SB.get_rankings_one("3DPrintGirl")
    print SB.get_rankings_one("shapeways", "all", "per_tweet")
    print SB.get_rankings_one("ozel", "5", "per_tweet")
    


""" Example score table:
score_table = {
    "maker1": { "overall": {'raw':100, 'per_tweet':2, 'per_word':0.1},
                "openness": {'raw':50, 'per_tweet':1.0, 'per_word':0.2}
                },
    "maker2": { "overall": {'raw':200, 'per_tweet':2, 'per_word':0.1},
                "openness": {'raw':50, 'per_tweet':1.0, 'per_word':0.3},
                "sustainability": {'raw':40, 'per_tweet':2.0, 'per_word':0.5}
                      }
}
"""

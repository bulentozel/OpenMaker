import random, math
from flask import jsonify, abort, request, make_response, url_for, render_template
from flask_service import *
from LibOM.Tools import *
from LibOM.GuiInterfaces import *
#from LibOM.GuiControlers import *

from bokeh.embed import components


DEFAULT_INF = "RealSexyCyborg"
DEFAULT_MEME = "craftship"
DEFAULT_CAT = "openmakership"
EXTERNAL_CAT = ["openness", "sharing", "innovation", "sustainability", "collectiveness"]

#ROOT_URL = "https://openmaker.herokuapp.com/"
ROOT_URL = "http://127.0.0.1:5000/"


def get_category_code(category):
    category = category.lower()
    code = MD.categories[category] if category in EXTERNAL_CAT else 'all'
    return code

def add_new_user(username):
    try:
        tdata = ClientTwitter.accumulate_auser_tweets(username, nlatest=50)
    except Exception:
        tdata = {"ntweets": 0, "content": ''}
    ntweets = tdata['ntweets']
    if not ntweets:
        message = username + " user doesn't exist or the account's tweets are not accessable at the moment."
        abort(400, message)

    text = tdata['content']
    nmappings, nwords, counts = extract_features(text, MD)
    features = {"source":1, "ntweets":ntweets, "nwords":nwords, "nmappings":nmappings, "counts":counts}
    SB.add_actor(username, features)
    print "New influencer on the board: ", username, ntweets, nmappings, nwords
 
    
def get_scores(username):
    if not SB.is_on_board(username): add_new_user(username)
    
    score = SB.get_score_one(username, 'all', 'per_tweet')
    categories = [get_category_code(cat) for cat in EXTERNAL_CAT]
    sub_scores = SB.get_scores(username, categories, 'per_tweet')
    sub_scores = {MD.get_category_name(k):v for k,v in sub_scores.items() if v}
    sub_total =  reduce(lambda x,y: x + y, [v for v in sub_scores.values() if v], 0.0)
    sub_scores['making'] = score - sub_total if sub_total < score else 0
    SB.update_the_board()
    result = {
        "overall":score,
        "ntweets":SB.table[username]['ntweets'],
        "compositions":sub_scores}
    return result


@auth.get_password
def get_password(username):
    if username == 'bulent':
        return 'flask'
    if username == 'openmaker':
        return '123456'
    return None


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)
    # 403 instead of 401 to prevent browsers from displaying the default auth dialog


@app.errorhandler(400)
def bad_request(error):
    response = jsonify({'message': error.description})
    response.status_code = 400
    #response.status = 'error.Bad Request'
    return response
    
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


   
@app.route('/')
def home():
    return make_response(jsonify(
        {"status":"OpenMaker.EU meme analysis server is UP.",
         "categories": EXTERNAL_CAT}),
                         200)


@app.route('/scoreboard', methods=['GET'])
def overall_scores():
    code = 'all'
    category = DEFAULT_CAT
    rankings = SB.get_rankings_one(code)
    rankings = map(lambda x: {"username":x[0], "score":x[1]}, rankings)
    return make_response(jsonify({
        "type":category,
        "rankings":rankings}),200)

#'<category>:{overall,openness,sustainability,sharing,democracy}'
@app.route('/scoreboard/<category>', methods=['GET'])
#@auth.login_required
def get_ranked_scores(category):
    code = get_category_code(category)
    if code == 'all': category = DEFAULT_CAT
    rankings = SB.get_rankings_one(code)
    rankings = map(lambda x: {"username":x[0], "score":x[1]}, rankings)
    return make_response(jsonify({
        "type":category,
        "rankings":rankings}),200)


@app.route('/influencer/<username>', methods=['GET'])
#@auth.login_required
def get_user_score(username):
    print "JSON query for Influencer", username
    
    result = get_scores(username)
    
    return make_response(jsonify({
        "influencer":username,
        "openmakership":result['overall'],
        "ntweets":result['ntweets'],
        "compositions":result['compositions']}),200)


@app.route('/refresh', methods=['GET'])
@auth.login_required
def refresh():
    influencers = SB.get_names(src='all')
    print influencers
    usernames = influencers.keys()
    debates = ClientTwitter.retrieve_tweets(usernames, 200)
    try:
        SB.import_board("./data/scoreboard.p")
    except IOError:
        print "No previously stored Scoreboard is found."


    # Re-populating the score board:
    print "The user data is being retrieved from Twitter: "
    for inf in debates.keys():
        ntweets = debates[inf]['ntweets']
        if not ntweets: continue
        text = debates[inf]['content']
        nmappings, nwords, counts = extract_features(text, MD)
        src = influencers[inf]
        features = {"source":src, "ntweets":ntweets, "nwords":nwords, "nmappings":nmappings, "counts":counts}
        SB.post_scores(inf, features)
        print inf, src, ntweets, nmappings, nwords

    # Re-store the baord:
    SB.store_the_board("./data/scoreboard.p")

    return make_response(jsonify(
       {"status":"The scoreboard is refreshed.",
        "influencers":usernames}),
                        200)

@app.route('/clean', methods=['GET'])
@auth.login_required
def clean():
    actorlist = SB.get_names(src=1)
    print actorlist
    actorlist = actorlist.keys()
    SB.remove(actorlist)
    # Restore the baord:
    SB.store_the_board("./data/scoreboard.p")
    ADDED = list()
    return make_response(jsonify(
       {"status":"User added names are removed from the board.",
        "removed":actorlist}),
                        200)

### VISUALIZATION RELATED INTERFACES
# Data static interface. It doesn't attempt to connect Twitter or WatchTower.
@app.route('/gui/datastatic', methods=["GET"])
def bokeh_static():
    SB = ScoreBoard()
    MD = MakerDictionary()
    board = SB.import_board("./data/scoreboard.p")
    layout = bokehGUI(SB, MD, offlineboard=board, curMeme=DEFAULT_MEME,
             curInfluencer=DEFAULT_INF)
    script, div = components(layout)
    return render_template("gui.html", script=script, div=div)

@app.route('/gui', methods=["GET"])
def bokeh():
    board = SB.import_board("./data/scoreboard.p")
    layout = bokehGUI(SB, MD, offlineboard=board, curMeme=DEFAULT_MEME,
             curInfluencer=DEFAULT_INF)
    script, div = components(layout)
    return render_template("gui.html", script=script, div=div)

@app.route('/gui/<name>', methods=["GET"])
def bokeh_query(name):
    get_scores(name)
    board = SB.import_board("./data/scoreboard.p")
    if SB.is_on_board(name):
        layout = bokehGUI(SB, MD, offlineboard=board, curMeme=DEFAULT_MEME, curInfluencer=name)
    else:
        layout = bokehGUI(SB, MD, offlineboard=board, curMeme=DEFAULT_MEME,
             curInfluencer='mbanzi')
    script, div = components(layout)
    return render_template("gui.html", script=script, div=div)

@app.route('/gui/api/<name>', methods=["GET"])
def bokeh_api(name):
    get_scores(name)
    board = SB.import_board("./data/scoreboard.p")
    if SB.is_on_board(name):
        layout = bokehGUI(SB, MD, offlineboard=board, curMeme=DEFAULT_MEME, curInfluencer=name, ApiRequest=True)
        script, div = components(layout)
        return(render_template("gui.html", script=script, div=div))
    else:
        message = name + " user doesn't exist or the account's tweets are not accessable at the moment."
        abort(400, message)


### The intefaces below are provided for backward compatibility.

# Influencer pages
@app.route('/gui/influencer/<name>', methods =["GET"])
def bokeh_inf(name):
    board = SB.import_board("./data/scoreboard.p")
    if name in SB.get_names(src='all').keys():
        layout = bokehGUI(SB, MD, offlineboard=board, curInfluencer=name)
    else:
        layout = bokehGUI(SB, MD, offlineboard=board)
    script, div = components(layout)
    return render_template("gui.html", script=script, div=div)

# Scoreboard pages
@app.route('/gui/scoreboard/<category>', methods=["GET"])
def bokeh_board(category):
    board = SB.import_board("./data/scoreboard.p")
    category = category.lower()
    if category in MD.categories.keys():
        layout = bokehGUI(SB, MD, offlineboard=board, curMeme=category)
    else:
        layout = bokehGUI(SB, MD, offlineboard=board)
    script, div = components(layout)
    return render_template("gui.html", script=script, div=div)

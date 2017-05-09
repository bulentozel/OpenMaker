import random
from flask import jsonify, abort, request, make_response, url_for
from flask_service import *
from LibOM.Tools import *

DEFAULT_CAT = "openmakership"
EXTERNAL_CAT = ["openness", "sharing", "innovation", "sustainability", "collectiveness"]

def get_category_code(category):
    category = category.lower()
    code = MD.categories[category] if category in EXTERNAL_CAT else 'all'
    return code
    
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

@app.route('/update', methods=['GET'])
@auth.login_required
def update():
    
   return make_response(jsonify(
       {"status":"The scoreboard is refreshed."}),
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
    print "Query Influencer", username
    if not SB.is_on_board(username):
        try:
            tdata = ClientTwitter.accumulate_auser_tweets(username)
        except Exception:
            tdata = {"ntweets": 0, "content": ''}
        ntweets = tdata['ntweets']
        if not ntweets:
            message = username + " user doesn't exist or has not tweeted at all."
            abort(400, message)

        text = tdata['content']
        nmappings, nwords, counts = extract_features(text, MD)
        features = {"ntweets":ntweets, "nwords":nwords, "nmappings":nmappings, "counts":counts}
        SB.add_actor(username, features)
        print "New influencer on the board: ", username, ntweets, nmappings, nwords
        
    score = SB.get_score_one(username, 'all', 'per_tweet')
    categories = [get_category_code(cat) for cat in EXTERNAL_CAT]
    sub_scores = SB.get_scores(username, categories, 'per_tweet')
    sub_scores = {MD.get_category_name(k):v for k,v in sub_scores.items() if v}
    sub_total =  reduce(lambda x,y: x + y, [v for v in sub_scores.values() if v], 0.0)
    sub_scores['making'] = score - sub_total if sub_total < score else 0
    return make_response(jsonify({
        "influencer":username,
        "openmakership":score,
        "ntweets":SB.table[username]['ntweets'],
        "compositions":sub_scores}),200)


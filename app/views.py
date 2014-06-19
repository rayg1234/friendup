from flask import render_template, flash, redirect, jsonify, request
from app import app
#host, port, user, passwd, db
from forms import LoginForm
from app.helpers.database import con_db

import pymysql
import gensim.models.word2vec as W2V
from dbconfig import theconfig
import GetMatch
from Utils import removeNonAscii

# To create a database connection, add the following
# within your view functions:
# con = con_db(host, port, user, passwd, db)
cur = GetMatch.GetConnection()
model1 = W2V.Word2Vec.load_word2vec_format('vectors7850.bin', binary=True)

# ROUTING/VIEW FUNCTIONS
@app.route('/', methods =['GET', 'POST'])
@app.route('/index', methods =['GET', 'POST'])
def index():

	return render_template('/index.html')

@app.route('/generate_match')
def generate_match():
	#get your user info
	
	#get the interests to match to
    	primeint = request.args.get('primeint', 0, type=str)
	int1 = request.args.get('int1', 0, type=str)
	int2 = request.args.get('int2', 0, type=str)
	int3 = request.args.get('int3', 0, type=str)

	topinterests = []
	if(int1 != '' or int1 is None):
		topinterests.append(int1)
	if(int2 != '' or int2 is None):
		topinterests.append(int2)
	if(int3 != '' or int3 is None):
		topinterests.append(int3)

	if(topinterests == []):
		return "null"

	

	#get the primary interest set with high fidelity
	primary_intset = GetMatch.GenerateInterestSet([primeint],model1,0.55)
	topintsets =[]
	for i in topinterests:
	    topintsets.append(GetMatch.GenerateInterestSet([i],model1,0.45))
	intset_all = GetMatch.GenerateInterestSet(topinterests,model1,0.45)

	#get subset of primary matches
	primarymatches = GetMatch.MatchOnInterests(cur,primary_intset,limit=10000)
	PIDS = [x[2] for x in primarymatches]
	
	#get refined matches on other matches
	r = GetMatch.MatchOnInterests_subset(cur,intset_all,PIDS,limit=10)

	allsets = []
	allsets.append(primary_intset)
	y = [allsets.append(x) for x in topintsets]
	#print allsets
	r,intersects = GetMatch.ReFactorScores_Balanced(cur,r,allsets)

	#start with r[0]
	ret = {}
	for i,currentmatch in enumerate(r):
		#currentmatch = r[0]
		curmatchPID = currentmatch[0]

		matchphotos = GetMatch.GetPhoto_byPID(cur,curmatchPID)
		if(matchphotos == []):
			matchphoto = "/static/happyface1.jpg"
		else:
			matchphoto = matchphotos[0]
		matchname = currentmatch[1]
		matchloc = GetMatch.GetLocation_byPID(cur,curmatchPID)

		#matchset_top = list(GetMatch.GetIntersect(cur,primary_intset,curmatchPID))
		#matchset_rest = []

		#for curset in topintsets:
		#	theintersect = GetMatch.GetIntersect(cur,curset,curmatchPID)
			#intersect1 = []
			#for x in theintersect:
			#	intersect1.append(x.encode('ascii', 'ignore'))
		#	matchset_rest.append(list(theintersect))
		
		ret[i] = {'photo':{'you':"/static/happyface1.jpg",'match':matchphoto},\
			'name':{'you':'You','match':removeNonAscii(matchname)},\
			'matchset_rest': {'you':'a','match':intersects}, \
			'link': {'you':'#','match':"http://www.meetup.com/members/" + str(curmatchPID)}, \
			'location': {'you':'#','match':matchloc}}


    	return jsonify(ret)

@app.route('/_add_numbers')
def add_numbers():
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result=a + b)

@app.route('/home')
def home():
    # Renders home.html.
	return render_template('home.html')

@app.route('/slides')
def about():
    # Renders slides.html.
	return render_template('slides.html')

@app.route('/author')
def contact():
    # Renders author.html.
    return render_template('author.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

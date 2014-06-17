from flask import render_template, flash, redirect, jsonify, request
from app import app
#host, port, user, passwd, db
from forms import LoginForm
from app.helpers.database import con_db

import pymysql
import gensim.models.word2vec as W2V
from dbconfig import theconfig
import GetMatch

# To create a database connection, add the following
# within your view functions:
# con = con_db(host, port, user, passwd, db)
cur = GetMatch.GetConnection()
model1 = W2V.Word2Vec.load_word2vec_format('vectors7850.bin', binary=True)

# ROUTING/VIEW FUNCTIONS
@app.route('/', methods =['GET', 'POST'])
@app.route('/index', methods =['GET', 'POST'])
def index():
	form = LoginForm()
	total = 0
	
	if form.validate_on_submit():
		print "valid"
		#get all other ints
		interest1 = form.Interest1.data
		topinterests = []
		topinterests.append(form.Interest2.data)
		topinterests.append(form.Interest3.data)
		topinterests.append(form.Interest4.data)

		#get the primary interest set with high fidelity
		primary_intset = GetMatch.GenerateInterestSet([interest1],model1,0.60)
		topintsets =[]
		for i in topinterests:
		    topintsets.append(GetMatch.GenerateInterestSet([i],model1,0.55))
		intset_all = GetMatch.GenerateInterestSet(topinterests,model1,0.55)


		#get subset of primary matches
		primarymatches = GetMatch.MatchOnInterests(cur,primary_intset,limit=10000)
		PIDS = [x[2] for x in primarymatches]
		
		#get refined matches on other matches
		r = GetMatch.MatchOnInterests_subset(cur,intset_all,PIDS,limit=20)
		

		#start with r[0]

		currentmatch = r[0]
		matchphoto = GetMatch.GetPhoto_byPID(cur,currentmatch[0])
		matchname = currentmatch[1]
		matchset_top = GetMatch.GetIntersect(cur,primary_intset,currentmatch[0])
		matchset_rest = []
		#print currentmatch[0]
		#print matchset_top
		for curset in topintsets:
			theintersect = GetMatch.GetIntersect(cur,curset,currentmatch[0])
			matchset_rest.append(theintersect)
			#print(theintersect)
		#print matchset_rest
		results = {'key':'value'}

		return render_template('/index.html',form=form,results = results)
	return render_template('/index.html', title ='Test',form = form)

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

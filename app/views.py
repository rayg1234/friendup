from flask import render_template, flash, redirect
from app import app
#host, port, user, passwd, db
from forms import LoginForm
from flask import request
from app.helpers.database import con_db
from forms import LoginForm

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
		#flash('Login requested for OpenID="' + form.openid.data + '", remember_me=' + str(form.remember_me.data))
		#print form.PID1.data
		#print form.Interest1.data
		res,total,photolink,yourname,matchname = GetMatch.MatchOnInterest(cur,form.PID1.data,form.Interest1.data);
		
		#flash('Match Name =' + res[0][0] + '", remember_me=' + str(form.remember_me.data))
		#print res
		#print total
		return render_template('/TestTemp.html',res = res, total = total,photolink = photolink, matchname = matchname,yourname = yourname)
	return render_template('/index.html', title ='Test',form = form)

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

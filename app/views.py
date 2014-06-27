from flask import render_template, flash, redirect, jsonify, request
from app import app
from app.helpers.database import con_db

import pymysql
import gensim.models.word2vec as W2V
import GetMatch
from Utils import removeNonAscii
import pickle
import numpy
from Timer import tic,toc

#load the interest to group conversion dictionary
with open('app/static/data/int_to_groups_w2v') as f:
    scaleddict_int_to_groups = pickle.load(f)[0]

with open('app/static/data/groupids_names_public') as f:
    gids_names = pickle.load(f)[0]

with open('app/static/data/Interest_to_IID') as f:
    Interest_to_IID = pickle.load(f)[0]

matchobj = GetMatch.GetMatch()
model1 = W2V.Word2Vec.load_word2vec_format('app/static/data/vectors7850.bin', binary=True)

print "All Data Loaded"

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
	primary_intset_expanded = matchobj.ExpandInterestSet([primeint],model1,0.55)
	top_intsets_expanded =[]
	for i in topinterests:
	    top_intsets_expanded.append(matchobj.ExpandInterestSet([i],model1,0.45))
	intset_all = matchobj.ExpandInterestSet(topinterests,model1,0.45)

	#get subset of primary matches
	tic()
	intids = [Interest_to_IID[x.replace("_"," ")] for x in primary_intset_expanded if x.replace("_"," ") in Interest_to_IID]
	primarymatches = matchobj.MatchOnInterests(intids,limit=1000)
	PIDS = [x[2] for x in primarymatches]
	toc()
	#get refined matches on other matches
	tic()
	intids = [Interest_to_IID[x.replace("_"," ")] for x in intset_all if x.replace("_"," ") in Interest_to_IID]
	r = matchobj.MatchOnInterests_subset(intids,PIDS,limit=20)
	toc()
	
	
	tic()
	#get a list of the expanded set of all interests	
	allintsets_expanded = []
	allintsets_expanded.append(primary_intset_expanded)
	y = [allintsets_expanded.append(x) for x in top_intsets_expanded]

	groupset_expanded = matchobj.ExpandGroups(allintsets_expanded,scaleddict_int_to_groups)
	

	#print groupset

	#r,intersects,sorted_scorecount = matchobj.ReFactorScores_Balanced(r,allintsets_expanded,groupset_expanded)

	intersecting_groups,groupscores = matchobj.Get_Intersecting_Groups(r,groupset_expanded)
	
	intersecting_ints,intscores = matchobj.Get_Intersecting_Intersets(r,allintsets_expanded)
	
	bscores = matchobj.Reorder_matches(groupscores,intscores)
	toc()
	
	reordered_matches = [x for (y,x) in sorted(zip(bscores,r),reverse=True)]
	reordered_intersecting_ints = [x for (y,x) in sorted(zip(bscores,intersecting_ints),reverse=True)]
	reordered_intersecting_groups = [x for (y,x) in sorted(zip(bscores,intersecting_groups),reverse=True)]
	reordered_intscores = [x for (y,x) in sorted(zip(bscores,intscores),reverse=True)]
	reordered_groupscores = [x for (y,x) in sorted(zip(bscores,groupscores),reverse=True)]


	#print reordered_intersecting_groups [0][0]
	#start with r[0]
	ret = {}
	for i,currentmatch in enumerate(reordered_matches):

		curmatchPID = currentmatch[0]

		matchphotos = matchobj.GetPhoto_byPID(curmatchPID)
		if(matchphotos == []):
			matchphoto = "/static/happyface1.jpg"
		else:
			matchphoto = matchphotos[0]
		matchname = currentmatch[1]
		matchloc = matchobj.GetLocation_byPID(curmatchPID)
		#matchgroups = GetMatch.GetGroups_byPID(cur,curmatchPID)
		
		groupnames = [[gids_names[m] for m in x] for x in reordered_intersecting_groups[i]]	
		
		ret[i] = {'photo': matchphoto,\
			'name': removeNonAscii(matchname),\
			'matchset_rest': reordered_intersecting_ints[i], \
			'link': "http://www.meetup.com/members/" + str(curmatchPID), \
			'location': matchloc, \
			'groupname': groupnames, \
			'catagories': [primeint]+topinterests, \
			'scores': list(numpy.array(reordered_intscores[i]) + numpy.array(reordered_groupscores[i])) }
	

    	return jsonify(ret)

@app.route('/home')
def home():
    # Renders home.html.
	return render_template('home.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

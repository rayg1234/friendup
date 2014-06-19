import pymysql
#import gensim
from dbconfig import theconfig

#conn = pymysql.connect(host=theconfig['host'], port=theconfig['port'], user=theconfig['user'], passwd=theconfig['password'], db=theconfig['database'])

def GetConnection():
	conn = pymysql.connect(host=theconfig['host'], port=3306, user=theconfig['user'], passwd=theconfig['password'], db=theconfig['database'])
	cur = conn.cursor()
	return cur

def CloseConnection(conn,cur):
	cur.close()
	conn.close()

def GenerateInterestSet(PrimaryInts,model,cutoff):
	intset = []
	modelcutoff = cutoff
	for r in PrimaryInts:
		if(r == '' or r is None):
			continue;
		try:
			sims = model.most_similar(positive=[r.replace(" ","_")],topn=10)
			[intset.append((x[0])) for x in sims if x[1] > modelcutoff]
			intset.append(r)
		except(KeyError):
			print str(KeyError) + " " + str(r)
		
	intset = list(set(intset))
	#print intset
	return intset

def MatchOnInterests(cur,theinterests,**kwargs):
	lim = kwargs.get('limit',None) #total results to return
	if lim is None:
		lim = 10
	if(theinterests == []):
		print "Null interests"
		return []
	x = ''
	for r in theinterests:
    		x +=  "\'" + r.replace("'","''") + "\',"

	theq = "select \
    			count(*), PName,PID \
		from \
    			PeopleLikeInterestsAL7 \
		where \
    			IName in (%s) \
		group by PID \
		order by count(*) desc \
		limit %s" % (x[0:-1].replace("_"," "),lim)
	#print theq
	cur.execute(theq)
	res = cur.fetchall() #returns a list of matches (# in common, Name, PID)
	return [x for x in res]

def MatchOnInterests_subset(cur,theinterests,subsetIDs,**kwargs):
	lim = kwargs.get('limit',None) #total results to return
	if lim is None:
		lim = 10
	if(theinterests == []):
		print "Null interests"
		return []
	x = ''
	for r in theinterests:
    		x +=  "\'" + r.replace("'","''") + "\',"

	ids = ''
	for r in subsetIDs:
	    ids += str(r) + ","
	

	theq = "SELECT PID,PName,count(*) from PeopleLikeInterestsAL7 \
		where IName in (%s) and \
		PID in (%s)\
		group by PID \
		order by count(*) desc\
		limit %s" % (x[0:-1].replace("_"," "),ids[0:-1],lim)

	cur.execute(theq)
	res = cur.fetchall() #returns a list of matches (# in common, Name, PID)
	return [x for x in res]



def GetIntersect(cur,interestset,matchID):
	curset = GetInterests_byPID(cur,matchID)
	interestset = [x.replace("_"," ") for x in interestset]
	return set(curset).intersection(set(interestset))

def GetGroupIntersect_byPID(cur,groupids,PID):
	if(groupids == []):
		print "Null interests"
		return []
	x = ''
	for r in groupids:
    		x +=  "\'" + str(r) + "\',"

	theq = "select GID from PeopleGroups where PID = %s and GID in (%s)" % (str(PID),x[0:-1])

	#print theq
	cur.execute(theq)
	res = cur.fetchall()
	return [x[0] for x in res]

def ReFactorScores_Balanced(cur,matches,intsets,**kwargs):
	#print intsets
	scorecount = []
	bscore = []
	theintersects = []
	for r in matches:
		curintersect = [list(GetIntersect(cur,x,r[0])) for x in intsets]

		theintersects.append(curintersect)
		thescores = [len(x) for x in curintersect]
		scorecount.append(thescores)
		y = 1.0
		for x in thescores:
			y = (x+1)*y
		bscore.append(y**(0.25))
	sorted_bscore, sorted_matches,sorted_scorecount ,sorted_intersects = zip(*sorted(zip(bscore,matches,scorecount,theintersects),reverse=True))
	#print sorted_scorecount
	#print sorted_intersects
	return sorted_matches,sorted_intersects
	


	

def CreateSubsetView(cur,theinterests,viewname,**kwargs):
	lim = kwargs.get('limit',None) #total results to return
	if lim is None:
		lim = 10
	if(theinterests == []):
		print "Null interests"
		return []
	x = ''
	for r in theinterests:
    		x +=  "\'" + r + "\',"

	theq = "create view sub1 as ( \
			select \
    				PID, PName \
			from \
    				PeopleLikeInterestsAL7 \
			where \
    				IName in (%s) \
			limit %s \
			);" % (x[0:-1].replace("_"," "),lim)
	#print theq
	cur.execute(theq)
	return

def DropView(cur,viewname):
	theq = "drop view %s" % (viewname)
	cur.execute(theq)
	return

def GetGroups_byPID(cur,PID):
	theq = "select GID from PeopleGroups where PID = %s" % str(PID)
	cur.execute(theq)
	res = cur.fetchall()
	return [x[0] for x in res]

def GetInterests_byPID(cur,PID):
	theq = "select IName from PeopleLikeInterestsAL7 where PID = %s" % str(PID)
	cur.execute(theq)
	res = cur.fetchall()
	return [x[0] for x in res]
	
def GetPhoto_byPID(cur,PID):
	theq = "select Photolink from Photos where PID=%s" % str(PID)
	cur.execute(theq)
	res = cur.fetchall()
	return [x[0] for x in res]

def GetLocation_byPID(cur,PID):
	theq = "select Location from People where PID=%s" % str(PID)
	cur.execute(theq)
	res = cur.fetchall()
	if len(res[0])>0:
		return res[0][0]
	else:
		return ''



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
		try:
			sims = model.most_similar(positive=[r.replace(" ","_")],topn=10)
			[intset.append((x[0])) for x in sims if x[1] > modelcutoff]
		except(KeyError):
			print str(KeyError) + " " + str(r)
		
	intset = list(set(intset))
	print intset
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
    		x +=  "\'" + r + "\',"

	theq = "select \
    			count(*), PName,PID \
		from \
    			PeopleLikeInterestsAL7 \
		where \
    			IName in (%s) \
		group by PID \
		order by count(*) desc \
		limit %s" % (x[0:-1].replace("_"," "),lim)
	cur.execute(theq)
	res = cur.fetchall() #returns a list of matches (# in common, Name, PID)
	return [x for x in res]

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

	theq2 = "create view %s as ( \
			select \
    				PeopleLikeInterestsAL7.PID, PeopleLikeInterestsAL7.PName, PeopleLikeInterestsAL7.IID, IName \
			from \
    				sub1 \
        		join \
    				PeopleLikeInterestsAL7 ON PeopleLikeInterestsAL7.PID = sub1.PID);" % (viewname)
	cur.execute(theq2)
	theq3 = "drop view sub1;"
	cur.execute(theq3)
	return

def DropView(cur,viewname):
	theq = "drop view %s" % (viewname)
	cur.execute(theq)
	return

def GetInterests_byPID(cur,PID):
	theq = "select IName from PeopleLikeInterestsAL7 where PID = %s" % str(PID)
	cur.execute(theq)
	res = cur.fetchall()
	return [x[0] for x in res]
	
def GetPhoto_byPID(cur,PID):
	theq = "select Photolink from Photos where PID=%s" % str(PID)
	cur.execute(theq)
	res = cur.fetchall()
	print [x[0] for x in res]

#too slow, do not use!
def MatchOnMember(cur,thepid,theinterest):

	
	theq = "select B.PID,count(B.IID) as theCount \
		from \
		( \
		SELECT PID,IID,IName \
		FROM PeopleLikeInterests \
		where PID='%s' \
		) as A \
		join \
		( \
		select A.PID,Likes.IID \
		from \
		(select PID \
		from PeopleLikeInterests \
		Where IName = '%s') as A \
		join Likes \
		on A.PID = Likes.PID \
		) as B \
		on A.IID = B.IID and A.PID != B.PID \
		group by B.PID \
		Order by theCount Desc \
		Limit 1" % (thepid,theinterest)
	
	cur.execute(theq)
	res = cur.fetchall()
	if(res == ()):
		return "No Match :(",0,0,0,0
	else:
		totalcom = res[0][1]
		thematchid = str(res[0][0])

		theq = "select PName from People where PID='%s'" % (thepid)
		cur.execute(theq)
		res = cur.fetchall()
		yourname = res[0][0];
		print yourname

		theq = "select PName from People where PID='%s'" % (thematchid)
		cur.execute(theq)
		res = cur.fetchall()
		matchname = res[0][0];

		theq = "select Photolink from Photos where PID='%s'" % (thematchid)
		cur.execute(theq)
		res = cur.fetchall()
		photolink = res[0][0];
		print photolink	
	
		theq = "select PName,IName from PeopleLikeInterests where PID='%s'" % (thematchid)
		cur.execute(theq)
		res = cur.fetchall()
		return res,totalcom,photolink,yourname,matchname
	



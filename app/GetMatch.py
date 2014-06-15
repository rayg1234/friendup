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
		sims = model.most_similar(positive=[r],topn=10)
		[intset.append((x[0])) for x in sims if x[1] > modelcutoff]
	intset = list(set(intset))
	return intset

def MatchOnInterests(cur,theinterests):
	x = ''
	for r in intset:
    		x +=  "\'" + r + "\',"

	theq = "select \
    			count(*), PName,PID \
		from \
    			PeopleLikeInterestsAL7 \
		where \
    			IName in (%s) \
		group by PID \
		order by count(*) desc \
		limit 10" % (x[0:-1].replace("_"," "))
	cur.execute(theq)
	res = cur.fetchall() #returns a list of matches (# in common, Name, PID)
	return [x for x in res]

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
	



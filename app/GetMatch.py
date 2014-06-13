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


def MatchOnInterest(cur,thepid,theinterest):

	
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
		return "No Match :(",0
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
	

	#cur.close()
	#conn.close()
	



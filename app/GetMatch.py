import pymysql
#import gensim
from dbconfig import theconfig

class GetMatch():

	def __init__(self):
		self.conn = pymysql.connect(host=theconfig['host'], port=3306, user=theconfig['user'], passwd=theconfig['password'], db=theconfig['database'])
		self.cur = self.conn.cursor()

	def CloseConnection(self,conn,cur):
		self.cur.close()
		self.conn.close()

	def ExpandInterestSet(self,theinterests,model,cutoff):
		intset = []
		modelcutoff = cutoff
		for r in theinterests:
			if(r == '' or r is None):
				continue;
			try:
				sims = model.most_similar(positive=[r.replace(" ","_")],topn=8)
				[intset.append((x[0])) for x in sims if x[1] > modelcutoff]
				intset.append(r)
			except(KeyError):
				print str(KeyError) + " " + str(r)
		
		intset = list(set(intset))

		return intset

	def ExpandGroups(self,intsets,int_to_groups):

		groupset = []
	
		for curset in intsets:
			curgroupset = set()
			for curint in curset:			
				if curint in int_to_groups:
					curgroupset = curgroupset.union([key for key,val in int_to_groups[curint].iteritems() if val>0.01])
			groupset.append(curgroupset)
	
		return groupset 

	def MatchOnInterests(self,theinterests,**kwargs):
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
		self.conn.ping(reconnect = True)
		self.cur.execute(theq)
		res = self.cur.fetchall() #returns a list of matches (# in common, Name, PID)
		return [x for x in res]

	def MatchOnInterests_subset(self,theinterests,subsetIDs,**kwargs):
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

		self.conn.ping(reconnect = True)
		self.cur.execute(theq)
		res = self.cur.fetchall() #returns a list of matches (# in common, Name, PID)
		return [x for x in res]

	def GetIntersect(self,interestset,matchID):
		curset = self.GetInterests_byPID(matchID)
		interestset = [x.replace("_"," ") for x in interestset]
		return set(curset).intersection(set(interestset))

	def GetGroupIntersect_byPID(self,groupids,PID):
		if(list(groupids) == []):
			print "Null interests"
			return []
		x = ''
		for r in groupids:
	    		x +=  "\'" + str(r) + "\',"

		theq = "select GID from PeopleGroups where PID = %s and GID in (%s)" % (str(PID),x[0:-1])

		#print theq
		self.conn.ping(reconnect = True)
		self.cur.execute(theq)
		res = self.cur.fetchall()
		return [x[0] for x in res]

	def Get_Intersecting_Intersets(self,matches,intsets):
		scorecount = [] #the 'score' for each category of interests
		theintersects = [] #intersecting interest sets

		for r in matches:
			curintersect = [list(self.GetIntersect(x,r[0])) for x in intsets]

			theintersects.append(curintersect)
			thescores = [len(x) for x in curintersect]
			scorecount.append(thescores)
	
		return theintersects,scorecount

	def Get_Intersecting_Groups(self,matches,groupsets):
		scorecount = [] #the 'score' for each category of interests
		groupintersects = [] #intersecting interest sets

		for r in matches:
			curintersect = [self.GetGroupIntersect_byPID(x,r[0]) for x in groupsets]
			groupintersects.append(curintersect)
			thescores = [len(x) for x in curintersect]
			scorecount.append(thescores)

		return groupintersects,scorecount

	def Reorder_matches(self,groupscores,intscores):
		bscores = []
		for i in range(0,len(intscores)):
			g = groupscores[i] #score for person i
			s = intscores[i]
			y = 1.0

			for j in range(0,len(s)):
				y = (g[j]+s[j]+1)*y
			bscores.append(y**(1/float(len(s))))

		return bscores

	def ReFactorScores_Balanced(self,matches,intsets,groupsets,**kwargs):

		scorecount = [] #the 'score' for each category of interests
		bscore = [] #the geometric mean score
		theintersects = [] #intersecting interest sets

		for r in matches:
			curintersect = [list(GetIntersect(x,r[0])) for x in intsets]

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
		return sorted_matches,sorted_intersects,sorted_scorecount

	def GetGroups_byPID(self,PID):
		theq = "select GID from PeopleGroups where PID = %s" % str(PID)
		#print theq
		self.conn.ping(reconnect = True)
		self.cur.execute(theq)
		res = self.cur.fetchall()
		return [x[0] for x in res]

	def GetInterests_byPID(self,PID):
		theq = "select IName from PeopleLikeInterestsAL7 where PID = %s" % str(PID)
		self.conn.ping(reconnect = True)
		self.cur.execute(theq)
		res = self.cur.fetchall()
		return [x[0] for x in res]
	
	def GetPhoto_byPID(self,PID):
		theq = "select Photolink from Photos where PID=%s" % str(PID)
		self.conn.ping(reconnect = True)
		self.cur.execute(theq)
		res = self.cur.fetchall()
		return [x[0] for x in res]

	def GetLocation_byPID(self,PID):
		theq = "select Location from People where PID=%s" % str(PID)
		self.conn.ping(reconnect = True)
		self.cur.execute(theq)
		res = self.cur.fetchall()
		if res != () and len(res[0])>0:
			return res[0][0]
		else:
			return ''


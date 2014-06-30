# -*- coding: utf-8 -*-
"""
Created on Mon Jun  9 15:16:06 2014

@author: ray
"""

import json
import urllib
import urllib2
import pickle
import time
import random
import numpy
import mysql.connector
import os.path
import sys
import UtilFuns
import GeoDistance


cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()
#qe = "SELECT * FROM Members"
#cursor.execute(qe)

with open('/media/ray/Storage/Projects/Insight/Meetup/Data/groupids_shuffled') as f:
    gids_s = pickle.load(f)[0]
    
with open('/media/ray/Storage/Projects/Insight/Meetup/Data/groupids_names_public') as f:
    gids_names = pickle.load(f)[0]


for i in range(100,7850,100):
    
    endgroup = min(i+100,len(gids_s))
    startgroup = i
    
    membersdict = []
    interestsdict = []
    edgesdict = []
    biodict = []
    photodict = []
    #groupsdict = []
    peoplegroupdict = []
    
    UtilFuns.tic()
    
    for curgroup in range (startgroup,endgroup):
        
        curgid = gids_s[curgroup]
        currentoffset = 0
        print "prcessing group# " + str(curgroup) 
        while True:
            filestr = '/media/ray/Storage/Projects/Insight/Meetup/Data/AllGroupData/'+ "groupdata_"+str(curgid) + "_" + str(currentoffset)
            
            if os.path.isfile(filestr):
                with open(filestr) as f:
                    members = pickle.load(f)[0]
                    
                #print "Storing data into db..."
                total_count = members['meta']['total_count']
                #print "prcessing group# " + str(curgroup) + " ID: "+ str(curgid) + " Offset: "+ str(currentoffset) + " has " + str(members['meta']['total_count']) + " members"
                #sys.stdout.flush()
                
                
                for curmember in members['results']:
                    m_id = curmember['id']
                    if('name' in curmember):            
                        m_name = curmember['name']
                    else:
                        m_name = ''
                    if('city' in curmember):      
                        m_city = curmember['city']
                        lon = curmember['lon']
                        lat = curmember['lat']
                        distance = numpy.abs(GeoDistance.haversine(-122.40, 37.77,float(lon),float(lat)))
                        if(distance <= 75):
                            membersdict.append((str(m_id),m_name.replace("'","''"),m_city,lon,lat))
                            if('bio' in curmember):
                                biodict.append((str(m_id),str(curgid),curmember['bio']))
                            if('photo' in curmember):               
                                photodict.append((str(m_id),str(curgid),curmember['photo']['photo_link']))
                            peoplegroupdict.append((str(m_id),str(curgid)))
                            
                            for curinterest in curmember['topics']:
                                c_id = curinterest['id']
                                if('name' in curinterest): 
                                    c_name = curinterest['name'] 
                                else:
                                    c_name = ''
                                interestsdict.append((str(c_id),c_name.replace("'","''"),))
                                edgesdict.append((str(m_id),str(c_id)))
                    
                    #groupsdict.append((str(curgid),gids_names[curgid]))
                    
    
                currentoffset+=1
                    
            else:
                #print "requested file: " + filestr + " Not found"
                break
    
    members_unique = list(set(membersdict))
    interests_unique = list(set(interestsdict))
    edges_unique = list(set(edgesdict))
    #groupsdict_unique = list(set(groupsdict))
    peoplegroupdict_unique = list(set(peoplegroupdict))
    
    
    stmt1 = "INSERT IGNORE INTO People (PID,PName,Location,Lon,Lat) VALUES (%s,%s,%s,%s,%s)"
    cursor.executemany(stmt1,members_unique)
    
    stmt2 = "INSERT IGNORE INTO Interests (IID,IName) VALUES (%s,%s)"
    cursor.executemany(stmt2,interests_unique)
    
    stmt3 = "INSERT IGNORE INTO Likes (PID,IID) VALUES (%s,%s)"
    cursor.executemany(stmt3,edges_unique)
    
    stmt4 = "INSERT IGNORE INTO Bios (PID,GID,Bio) VALUES (%s,%s,%s)"
    cursor.executemany(stmt4,biodict)
 
    stmt5 = "INSERT IGNORE INTO Photos (PID,GID,PhotoLink) VALUES (%s,%s,%s)"
    cursor.executemany(stmt5,photodict)
   
    #stmt6 = "INSERT IGNORE INTO Groups (GID,GroupName) VALUES (%s,%s)"
    #cursor.executemany(stmt6,groupsdict_unique)
    
    stmt7 = "INSERT IGNORE INTO PeopleGroups (PID,GID) VALUES (%s,%s)"
    cursor.executemany(stmt7,peoplegroupdict_unique)
    
    cnx.commit()
    
    UtilFuns.toc()


cursor.close()
cnx.close()

#with open('/media/ray/Storage/Projects/Insight/Meetup/Data/EdgesData/edges3000') as f:
#    edges_u3000 = pickle.load(f)[0]

#with open('/media/ray/Storage/Projects/Insight/Meetup/Data/edges8000', 'w+') as f:
#    pickle.dump([edges_unique], f)

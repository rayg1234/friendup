# -*- coding: utf-8 -*-
"""
Created on Sun Jun  1 20:10:45 2014

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

cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

currentgroup = 0
currentoffset = 0

#load the shuffled gids
with open('/media/ray/Storage/Projects/Insight/Meetup/Data/groupids_shuffled') as f:
    gids_s = pickle.load(f)[0]
    
with open('/media/ray/Storage/Projects/Insight/Meetup/Data/crawlstate') as f:
    a = pickle.load(f)
    currentgroup = a[0]
    currentoffset = a[1]

totalgids = numpy.size(gids_s)
#for each group not crawled yet
while currentgroup < totalgids:

    #for key,val in enumerate(gids_s):
    curgid = gids_s[currentgroup]
    total_read_count = 0
    total_count = -1
    
    while total_read_count != total_count:
        #attempts to reopen the group data from local archives first
        filestr = '/media/ray/Storage/Projects/Insight/Meetup/Data/AllGroupData/'+ "groupdata_"+str(curgid) + "_" + str(currentoffset)
           
        if os.path.isfile(filestr):
            with open(filestr) as f:
                members = pickle.load(f)[0]
            
        else:
            print "attempting to retrieve group " + str(curgid) + " #:" + str(currentgroup) + " offset:" + str(currentoffset)
            sys.stdout.flush()     
            
            url = "http://api.meetup.com/2/members?"
            parameters = {"key": "7137559227cb4c53656271b5e531c",
                          "page":"200"}
            gid = {"group_id":curgid}
            offset = {"offset":currentoffset}
            parameters = dict(parameters.items() + gid.items() + offset.items())
            data = urllib.urlencode(parameters)
            urlx = url + data
            response = urllib2.urlopen(urlx)
            print "Response code: "+str(response.code)
            if response.code==200:
                members = json.load(response)
                
            else:
                print "Meetup request failed."
                break
        
        
            
    
        #dumps groupdata
        if not os.path.isfile(filestr):
            with open(filestr, 'w+') as f:
                pickle.dump([members], f)
        
        #for each member, store the member,interests into nodes in db and link them with edges
        print "Storing data into db..."
        total_count = members['meta']['total_count']
        print "group " + str(curgid) + " has " + str(members['meta']['total_count']) + " members"
        sys.stdout.flush()
        
        
        #This is very slow. Need to switch to batch executes      
#        for curmember in members['results']:
#            m_id = curmember['id']
#            m_name = curmember['name']
#            thenodeid1 = Meetup_dbfuncs.Db_Insert_Node(cursor,cnx,'Person',m_name.replace("'","''"),m_id)    
#            for curinterest in curmember['topics']:
#                cname = curinterest['name'] 
#                thenodeid2 = Meetup_dbfuncs.Db_Insert_Node(cursor,cnx,'Interest',cname.replace("'","''"),curinterest['id'])         
#                Meetup_dbfuncs.Db_Insert_Edge(cursor,cnx,thenodeid1,thenodeid2,'Like')

        #construct a list of members and ids (for inserting to nodes)
        #next construct list of interests and ids (for insert to nodes)
        #next construct list of edges and ids
        membersdict = []
        for curmember in members['results']:
            m_id = curmember['id']
            if('name' in curmember):            
                m_name = curmember['name']
            else:
                m_name = '_noname'
            membersdict.append(('Person',m_name.replace("'","''"),"Meetup_"+str(m_id)))
        
        interestsdict = []
        edgesdict = []
        for curmember in members['results']:
            m_id = curmember['id']
            for curinterest in curmember['topics']:
                c_id = curinterest['id']
                if('name' in curinterest): 
                    c_name = curinterest['name'] 
                else:
                    c_nmae = '_noname'
                interestsdict.append(('Interest',c_name.replace("'","''"),"Meetup_"+str(c_id)))
                edgesdict.append((("Meetup_"+str(m_id)),("Meetup_"+str(c_id))))
        
        
        
        stmt1 = "INSERT IGNORE INTO Nodes (Type,Name,ServiceTag) VALUES (%s,%s,%s)"
        cursor.executemany(stmt1,membersdict)
        cnx.commit()
        
        cursor.executemany(stmt1,interestsdict)
        cnx.commit()
        
        stmt2 = "SELECT * FROM Nodes WHERE ServiceTag=%s OR ServiceTag=%s"
        res = cursor.executemany(stmt2,edgesdict[0:2])
        
        
        ret = cursor.fetchmany()
        
        
        stmt3 = "SELECT * FROM Nodes WHERE ServiceTag='%s' OR ServiceTag='%s'" % ('Meetup_59258532', 'Meetup_15166')
        cursor.execute(stmt3)
        
        
        total_read_count += members['meta']['count']
        print "I read " + str(total_read_count)
        sys.stdout.flush()
        if(members['meta']['count']<=0):
            print "something went wrong with retrieving members..."
            break
        else:
            currentoffset += 1
        
        #writes the current crawl state to file
        with open('/media/ray/Storage/Projects/Insight/Meetup/Data/crawlstate', 'w+') as f:
            pickle.dump([currentgroup,currentoffset], f)
            
        print "Sleeping..."
        time.sleep(10)
    
    currentoffset = 0
    currentgroup+=1
    



cursor.close()
cnx.close()

#totints = 0
#for curmember in members['results']:
#    m_id = curmember['id']
#    m_name = curmember['name']
#    #thenodeid1 = Meetup_dbfuncs.Db_Insert_Node(cursor,cnx,'Person',m_name.replace("'","''"),m_id)    
#    for curinterest in curmember['topics']:
#        cname = curinterest['name']
#        totints+=1
#        #thenodeid2 = Meetup_dbfuncs.Db_Insert_Node(cursor,cnx,'Interest',cname.replace("'","''"),curinterest['id'])         
#        #Meetup_dbfuncs.Db_Insert_Edge(cursor,cnx,thenodeid1,thenodeid2,'Like')

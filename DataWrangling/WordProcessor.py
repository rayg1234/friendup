# -*- coding: utf-8 -*-
"""
Created on Wed Jun 18 21:58:03 2014

@author: ray
"""

from collections import Counter
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


with open('/media/ray/Storage/Projects/Insight/Meetup/Data/groupids_shuffled') as f:
    gids_s = pickle.load(f)[0]
    
with open('/media/ray/Storage/Projects/Insight/Meetup/Data/groupids_names_public') as f:
    gids_names = pickle.load(f)[0]
    
filegroupsize = 7850

interestsdict = []

wordcounts = Counter()

filestr_corpus =  '/media/ray/Storage/Projects/Insight/Meetup/w2vcorpus_incgids'

for curgroup in range (0,filegroupsize):
    curgid = gids_s[curgroup]
    currentoffset = 0
    
    while True:    
        filestr = '/media/ray/Storage/Projects/Insight/Meetup/Data/AllGroupData/'+ "groupdata_"+str(curgid) + "_" + str(currentoffset)
        s = ""    
        if os.path.isfile(filestr):
            with open(filestr) as f:
                members = pickle.load(f)[0]
                
            total_count = members['meta']['total_count']
            print "prcessing group# " + str(curgroup) + " ID: "+ str(curgid) + " has " + str(members['meta']['total_count']) + " members"
            #sys.stdout.flush()
                
            
            for curmember in members['results']:
                m_id = curmember['id']
                for curinterest in curmember['topics']:
                    c_id = curinterest['id']
                    if('name' in curinterest): 
                        c_name = curinterest['name'] 
                    else:
                        c_nmae = '_noname'
                    wordcounts.update([c_name])

 
                   
            #with open(filestr_corpus, 'a') as f:
            #    f.write(s)
                
            currentoffset+=1
                
        else:
            print "requested file: " + filestr + " Not found"
            break
        
with open('/media/ray/Storage/Projects/Insight/Meetup/Data/Interest_Counts', 'w+') as f:
    pickle.dump([wordcounts], f)
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 16:58:13 2014

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
import pandas
import gensim.models.word2vec as W2V

cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()
theq = "SELECT IID,IName FROM Interests"
    
cursor.execute(theq)
res = cursor.fetchall()

Interest_to_IID = dict()
IID_to_Interest = dict()

for r in res:
    IID_to_Interest[r[0]] = r[1]
    Interest_to_IID[r[1]] = r[0]


with open('/media/ray/Storage/Projects/Insight/Meetup/Data/scaleddict_group_to_ints2') as f:
    scaleddict_group_to_ints2 = pickle.load(f)[0]
    
with open('/media/ray/Storage/Projects/Insight/Meetup/Data/scaleddict_int_to_groups2') as f:
    scaleddict_int_to_groups2 = pickle.load(f)[0]
    
with open('/media/ray/Storage/Projects/Insight/Meetup/Data/groupids_shuffled') as f:
    gids_s = pickle.load(f)[0]
    
with open('/media/ray/Storage/Projects/Insight/Meetup/Data/groupids_names_public') as f:
    gids_names = pickle.load(f)[0]
    


group_to_ints_w2v = dict()
int_to_groups_w2v = dict()

for w in gids_names:
    group_to_ints_w2v[w] = []

model1 = W2V.Word2Vec.load_word2vec_format('/media/ray/Storage/Projects/Insight/vectors7850.bin', binary=True)

for g in gids_s:
    
    #first get the top int according to frequency scale
    print gids_names[g]
    y = [x for x in scaleddict_group_to_ints2[g].iteritems()]
    if y==[]:
        continue
    mydb = pandas.DataFrame(y)
    s= mydb.sort(1,ascending=False)
    s.iloc[0]
    #fanout the top int
    mostsims = model1.most_similar(positive=[s.iloc[0].values[0].replace(" ","_")],topn=30)
    for m in mostsims:
        mrep = m[0].replace("_"," ")
        if m[1] > 0.5: #assign each int to group dict
                group_to_ints_w2v[g].append(mrep) #these are unique so no need for sets
                if m[0] in int_to_groups_w2v:
                    int_to_groups_w2v[mrep].append(g)
                else:
                    int_to_groups_w2v[mrep] = []
                    int_to_groups_w2v[mrep].append(g)
                
with open('/media/ray/Storage/Projects/Insight/Meetup/Data/group_to_ints_w2v', 'w+') as f:
    pickle.dump([group_to_ints_w2v], f)
    
with open('/media/ray/Storage/Projects/Insight/Meetup/Data/int_to_groups_w2v', 'w+') as f:
    pickle.dump([int_to_groups_w2v], f)
                
with open('/media/ray/Storage/Projects/Insight/Meetup/Data/IID_to_Interest', 'w+') as f:
    pickle.dump([IID_to_Interest], f)
    
with open('/media/ray/Storage/Projects/Insight/Meetup/Data/Interest_to_IID', 'w+') as f:
    pickle.dump([Interest_to_IID], f)
        



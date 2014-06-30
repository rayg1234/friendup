# -*- coding: utf-8 -*-
"""
Created on Wed Jun 11 23:54:52 2014

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

import gensim.models.word2vec as W2V

with open('/media/ray/Storage/Projects/Insight/Meetup/Data/Interest_Counts') as f:
    wordcounts = pickle.load(f)[0]
    
reduceddict = {}

for w in wordcounts.iteritems():
    if w[1] > 100:
        reduceddict[w[0]] = w[1]
        
with open('/media/ray/Storage/Projects/Insight/Meetup/Data/groupids_names_public') as f:
    gids_names = pickle.load(f)[0]



model1 = W2V.Word2Vec.load_word2vec_format('vectors7850.bin', binary=True)

a = model1.vocab
vocab = a.keys()

nodes = []
edges = []
vocab_dict = dict()
for i,x in enumerate(vocab):
        vocab_dict[x] = i


for r in reduceddict:
    if r in vocab:
        nodes.append([vocab_dict[r],r])
        mostsims = model1.most_similar(positive=[r],topn=20)
        for m in mostsims:
            if m[0] in reduceddict and m[1] > 0.4:
                edges.append([vocab_dict[r],vocab_dict[m[0]],m[1]])
                
nodes2 = []
edges2 = []

for r in vocab:
    mostsims = model1.most_similar(positive=[r],topn=20)
    y = sum(numpy.array([x[1] for x in mostsims])>0.4)
    if y>10:
        nodes2.append([vocab_dict[r],r])
        for m in mostsims:
            if m[0] in reduceddict and m[1] > 0.4:
                edges2.append([vocab_dict[r],vocab_dict[m[0]],m[1]])

############################## Clustering gephi by high connectivity nodes #########
intrank = []
for r in vocab:
    mostsims = model1.most_similar(positive=[r],topn=20)
    inf = 0
    for m in mostsims:
        inf += m[1]
    intrank.append([r,inf])
    
a = numpy.array(intrank)
b = a[:,1].astype('float')
topints =  a[b>14,0]

nodes3 = []
edges3 = []
for t in topints:
    mostsims = model1.most_similar(positive=[t],topn=20)
    nodes3.append([vocab_dict[t],t])
    for m in mostsims:
        if m[0] in topints and m[1] > 0.6:
            edges3.append([vocab_dict[t],vocab_dict[m[0]],'Undirected',m[1]])

################################################# export csv #########################

import csv
with open('Meetup_Int_nodes_1315Elems.csv', 'wb') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',')
    spamwriter.writerow(['id','label','weight'])
    for x in nodes5:
        spamwriter.writerow(x)
    
with open('Meetup_Int_edges_1315Elems.csv', 'wb') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',')
    spamwriter.writerow(['Source','Target','Type','Weight'])
    for x in edges5:
        spamwriter.writerow(x)


############################## Clustering gephi by popular nodes#########
config = {
  'user': 'root',
  'password': '',
  'host': 'localhost',
  'database': 'peopledatadb2',
  'port': '3306',
}

cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()
theq = "SELECT IID,IName,count(*) FROM PeopleLikeInterests \
        group by IID \
        having count(*) > 0 \
        limit 50000"
    
cursor.execute(theq)
res = cursor.fetchall()

topints_cardinal = [x[1] for x in res]
topints_cardinal_id = [x[0] for x in res]
topints_weights = [x[2] for x in res]
topints_weights,topints_cardinal,topints_cardinal_id =zip(*sorted(zip(topints_weights,topints_cardinal,topints_cardinal_id),reverse=True))


topints_dict = dict()
for i,x in enumerate(topints_cardinal):
        topints_dict[topints_cardinal[i]] = topints_cardinal_id[i]

topints_dictweight = dict()
for i,x in enumerate(topints_cardinal):
        topints_dictweight[topints_cardinal[i]] = topints_weights[i]

nodes4 = []
edges4 = []
for i,r in enumerate(topints_cardinal[0:10000]):
    if r.replace(" ","_") in vocab:
        mostsims = model1.most_similar(positive=[r.replace(" ","_")],topn=20)
        y = sum(numpy.array([x[1] for x in mostsims])>0.4)
        if y>10:
            nodes4.append([topints_cardinal_id[i],r,topints_weights[i] ])
            for m in mostsims:
                if m[0].replace("_"," ") in topints_cardinal[0:10000] and m[1] > 0.6:
                    edges4.append([topints_cardinal_id[i],topints_dict[m[0].replace("_"," ")],'Undirected',m[1]])
                
    
###########################################################################
intrank = []
for r in vocab:
    mostsims = model1.most_similar(positive=[r],topn=20)
    inf = 0
    for m in mostsims:
        inf += m[1]
    intrank.append([r,inf])
    
a = numpy.array(intrank)
b = a[:,1].astype('float')
topints_bycon =  a[b>14,0]
topints_byn = [x.replace(" ","_") for x in topints_cardinal[0:7000]] #17
topints_all = list(set(topints_bycon).intersection(set(topints_byn)))


nodes5 = []
edges5 = []
for t in topints_all:
    mostsims = model1.most_similar(positive=[t],topn=20)
    nodes5.append([topints_dict[t.replace("_"," ")],t.replace("_"," "),topints_dictweight[t.replace("_"," ")]])
    for m in mostsims:
        if m[0] in topints_all and m[1] > 0.5:
            edges5.append([topints_dict[t.replace("_"," ")],topints_dict[m[0].replace("_"," ")],'Undirected',m[1]])



y = [x.replace("_"," ") for x in topints_all]
import json
with open('NewDict3444.json', 'w') as outfile:
    json.dump(y, outfile)

################################# map INames to IIDs #####################################
    
with open('/media/ray/Storage/Projects/Insight/Meetup/Data/scaleddict_group_to_ints2', 'w+') as f:
    pickle.dump([scaleddict_group_to_ints], f)
    
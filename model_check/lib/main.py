#!/usr/bin/python3

##imports for config file
import argparse
import os
import yaml

# own classes and file imports
from classes.Document_Collection import *
from classes.BPMN import *
from classes.Process import *
from classes.Pair import *
from classes.SimilarityComputer import *
from functions import *

# imports for bpmnparser
from xml.dom import minidom
from collections import defaultdict

import spacy
import re

GATEWAYS = ["parallelGateway", "exclusiveGateway", "complexGateway", "eventBasedGateway", "inclusiveGateway"]

EVENTS = ["intermediateCatchEvent", "intermediateThrowEvent", "boundaryEvent"]

#################################################################

nlp = spacy.load('en_core_web_lg')

print("load success")

path1 = '.././input/'
path2 = '.././results/'
# input路径
modeldir = path1 + "models/gdpr/"
docdir = path1 + "regulations/gdpr/"
targetdir = path2 + "gdpr_gamma04/"

# nlp文件
signalwords_dir = path1 + "files/signalwords.txt"
sequencemarkers_dir = path1 + "files/sequencemarkers.txt"
stopwords_dir = path1 + "files/stopwords.txt"

spacy_cache = "./caches/spacysimcache_tasks_clauses.json"

# configration
collectionid = 0
only_constraints = True
gamma = 0.4
delta = 0.8

## parse Regulations ############################################

## paragraphs 字典将包含所有文本文件的内容，以文件名（不包括扩展名）作为键，可以通过键来访问每个文本文件的内容
paragraphs = dict()
files = os.listdir(docdir)
try:
    for fi in files:
        with open(docdir + fi, encoding='utf-8') as f:
            paragraphs[re.sub('\.txt', '', fi)] = f.read()  ## 将键去掉txt
except FileNotFoundError:
    print("wrong docdir")
    quit()
## signalwords 列表包含了从文件 signalwords_dir 读取的所有文本行。每个文本行作为列表中的一个字符串元素，可以随后用于进一步处理或分析信号词数据。
try:
    with open(signalwords_dir) as f:
        signalwords = f.read().splitlines()
except FileNotFoundError:
    print("wrong signalwords")
    quit()

try:
    with open(sequencemarkers_dir) as f:
        sequencemarkers = f.read().splitlines()
except FileNotFoundError:
    print("wrong sequencemarkers")
    quit()

try:
    with open(stopwords_dir) as f:
        stopwords = f.read().splitlines()
except FileNotFoundError:
    print("wrong stopwords")
    quit()

document_collection = Document_Collection(int(collectionid), paragraphs, signalwords, sequencemarkers,stopwords, nlp, only_constraints)

print("parse regulations sucess")

#################################################################


## parse BPMN files ############################################
try:
    bpmn_models = list()
    # 资源集合
    resource_set = set()
    for f in os.listdir(modeldir):
        if f.startswith('.'):
            continue
        # 利用minidom解析bpmn文件成一个dom树
        doc = minidom.parse(modeldir + f)
        processes_dom_elements = doc.getElementsByTagName("process")  ## 从XML文档中获取所有名为 "process" 的元素

        processes = list()  ## 创建一个空列表，用于存储BPMN流程的信息
        for p in processes_dom_elements:
            # 获得各个元素的信息
            # 得到process的id值
            _id = p.getAttribute("id")
            # 得到process的name值
            participant = p.getAttribute("name")
            # 得到startevents dom树
            start_events = p.getElementsByTagName("startEvent")
            end_events = p.getElementsByTagName("endEvent")
            tasks = p.getElementsByTagName("task")
            flows = p.getElementsByTagName("sequenceFlow")
            # 根据网关得到控制流信息
            gateways = defaultdict(list)
            # GATEWAYS = ["parallelGateway", "exclusiveGateway", "complexGateway", "eventBasedGateway", "inclusiveGateway"]
            for g in GATEWAYS:
                gateways[g] = p.getElementsByTagName(g)
            events = defaultdict(list)
            # EVENTS = ["intermediateCatchEvent", "intermediateThrowEvent", "boundaryEvent"]
            for e in EVENTS:
                events[e] = p.getElementsByTagName(e)
            #得到执行者信息
            resource_set.add(participant.lower())
            processes.append(
                Process(_id, nlp, stopwords_dir, participant, start_events, end_events, tasks, gateways, events, flows))
        bpmn_models.append(BPMN(f, processes))
except FileNotFoundError:
    print("wrong docdir")
    quit()

print("parse BPMN model sucess")
################################################################# END


# 初始化相似度计算
sim = SimilarityComputer(nlp, bpmn_models, document_collection, stopwords_dir, spacy_cache)

pairs_per_model = defaultdict(list)
for model in bpmn_models:
    for paragraph in document_collection.paragraphs:
        pairs_per_model[model._id].append(Pair(nlp, sim, model, paragraph, resource_set, gamma, delta))

evaluation_csv(targetdir, pairs_per_model)

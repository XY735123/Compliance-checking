import re
# import spacy
from collections import defaultdict

class Process:
  def __init__(self, _id, nlp, stopwords, participant, start_events, end_events, tasks, gateways, events, flows):
    self._id = _id
    self.nlp = nlp
    self.stopwords = stopwords
    self.participant = participant
    self.start_events = start_events
    self.end_events = end_events
    self.tasks = tasks
    self.gateways = gateways
    self.events = events
    self.flows = flows
    
    # set all labels ###############
    self.start_event_labels = list()
    self.end_event_labels = list()
    self.task_labels = list()
    self.event_labels = defaultdict(list)
    self.gateway_labels = defaultdict(list)
    self.set_labels()

    # calculate reachability and label lists  ###############
    self.directly_follows = self.compute_directly_follows()
    self.reachability = self.compute_reachability()
    self.obligation_list = self.calculate_obligation_list()
    self.obligation_list_labels = self.calculate_obligation_list_labels()
    self.obligation_list_labels_lemmatized = self.calculate_obligation_list_labels_lemmatized()

  
  def __repr__(self):
    s = "ID: " + self._id
    s += "\nParticipant: " + self.participant
    return s
    
  def set_labels(self):
    # 正则表达式，用于后续检测非空
    regexp = re.compile(r'.+')
    for element in self.start_events:
      # 提取element中的name
      l = element.getAttribute("name")
      # 判断是否非空
      if regexp.search(l):
        # 非空则将其加入标签list中
        self.start_event_labels.append(l)
    for element in self.end_events:
      l = element.getAttribute("name")
      if regexp.search(l):
        self.end_event_labels.append(l)
    for element in self.tasks:
      l = element.getAttribute("name")
      if regexp.search(l):
        self.task_labels.append(l)
    for k,v in self.events.items():
      for element in v:
        l = element.getAttribute("name")
        if regexp.search(l):
          self.event_labels[k].append(l)
    for k,v in self.gateways.items():
      for element in v:
        l = element.getAttribute("name")
        if regexp.search(l):
          self.gateway_labels[k].append(l)
  
  #assumption: obligations from a paragraph can be encoded within events and tasks 
  def calculate_obligation_list(self):
    labellist = self.start_events + self.end_events + self.tasks
    for k,ev in self.events.items():
      labellist.extend(ev)
    return labellist
   
  def calculate_obligation_list_labels(self):
    labellist = self.start_event_labels + self.end_event_labels + self.task_labels
    for k,ev in self.event_labels.items():
      labellist.extend(ev)
    return labellist

  def calculate_obligation_list_labels_lemmatized(self):
    labellist = self.obligation_list_labels
    result = list()
    for elem in labellist:  
      tmp = list()  
      words = self.nlp(elem)
      for w in words:
        if(w.lemma_ == "-PRON-"):
          tmp.append(w.text)
        else:
          if(w.is_punct or w.like_num or w.is_space or w.text in self.stopwords):
            continue
          tmp.append(w.lemma_)
      result.append(tmp)
    return result

  def compute_directly_follows(self):
      # 定义一个字典存储直接后继
      directly_follows = dict()
      # insert directly follows pairs
      for flow in self.flows:
        sourceid = flow.getAttribute("sourceRef")
        targetid = flow.getAttribute("targetRef")
        reachable = list()
        if sourceid in directly_follows:
          reachable = directly_follows[sourceid]
        reachable.append(targetid)
        directly_follows[sourceid] = reachable
      return directly_follows

  def compute_reachability(self):
      reachability_relation = dict()
      nodes = set()
      for key in self.directly_follows:
        nodes.add(key)
        nodes = nodes.union(self.directly_follows[key])

      for node in nodes:
        stack = list()
        stack.append(node)
        reachable = set()
        reachable.add(node)
        while stack:  # while stack is not empty
          current = stack.pop()
          if current in self.directly_follows:
            for follower in self.directly_follows[current]:
              if follower not in reachable:  # if not yet seen
                reachable.add(follower)
                stack.append(follower)
        reachability_relation[node] = reachable
      return reachability_relation

  def is_reachable_from(self, sourceid, targetid):
      if sourceid in self.reachability:
        # 错了
        # return targetid in self.reachability[targetid]
        return targetid in self.reachability[sourceid]
      return False

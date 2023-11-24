OBJECTS = ["dobj", "dative", "attr", "oprd", "pobj"]
TIME = ["year", "month", "day", "hour", "minute", "second"]
UNITS = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]
COMP = ["compound", "amod"]
VERB_MOD = ["aux", "acomp", "xcomp"]


class Clause:
  def __init__(self, _id, nlp, stopwords, clause): 
    self._id = _id
    self.nlp = nlp
    self.stopwords = stopwords
    self.clause = clause
    
    # setting subject, verb, object and rest is done in Sentence.py
    self.subject = None
    self.verb = None
    self.object = None
    self.rest = None
    
    self.lemmatized = self.clause_as_lemmatized_string()
    
    
  def __repr__(self):
    return "CLAUSE: " + self.clause_as_string() + "\nSUBJECT: " + self.subject_as_string() + "\nOBJECT: " + self.object_as_string() + "\nVERB: " + self.verb_as_string()  + "\nREST: " + self.rest_as_string()
    
  def __str__(self):
    return "CLAUSE: " + self.clause_as_string() + "\nSUBJECT: " + self.subject_as_string() + "\nOBJECT: " + self.object_as_string() + "\nVERB: " + self.verb_as_string()  + "\nREST: " + self.rest_as_string()
    
  def __add__(self, other):
    return str(self) + other
  
  def __radd__(self, other):
    return other + str(self)
    
    
  def set_subject(self, subject):
    self.subject = subject 

  def set_remaining(self):
    self.set_object()
    self.set_verb()
    indices = set()
    if(self.subject is not None):
      for token in self.subject:
        indices.add(token.i)
    if(self.object is not None):
      for token in self.object:
        indices.add(token.i)
    if(self.verb is not None):
      for token in self.verb:
        indices.add(token.i)
    self.set_rest(indices)

  def set_object(self):
    for token in self.clause:
      # 如果 1.宾语没被找到 2.该词的依赖关系在OBJECTS中 3.他的词性不是代词
      if(self.object is None and token.dep_ in OBJECTS and token.pos_ != "PRON"):
          # 如果上述条件都满足，那么将当前词语（token）以及 当前词语左边，在其子树中依赖关系为COMP的词语加入object列表中：
          self.object = [t for t in token.subtree if ((t.dep_ in COMP and t in token.lefts) or t == token)]
     
  def set_verb(self):
    new = self.nlp(self.clause_as_string())
    for n in new:
      # 找到从句中的根词（通常是主谓动词）
      if(n.dep_ == "ROOT"):
        root = n
    # 提取 1.与 root 相等并且词性是 "VERB"（主谓） 2.依存关系在 VERB_MOD 并且词性是 "VERB" 或 "ADJ"。 3.依存关系是 "auxpass"，同时 s 在 root 的左侧。 三者之一满足的作为verb
    self.verb = [s for s in root.subtree if((s == root and s.pos_ == "VERB") or (s.dep_ in VERB_MOD and s.pos_ == "VERB") or (s.dep_ in VERB_MOD and s.pos_ == "ADJ") or (s.dep_ == "auxpass" and s in root.lefts))]
  
  def set_time(self):
    # 存储从句中找到的与时间相关的词语的基本形式
    time_units = set()
    for token in self.clause:
      if(token.lemma_ in TIME):
        time_units.add(token.lemma_)
        # 查找与时间相关词汇的左侧依赖（left dependencies）
        left_dependencies =  [t for t in token.lefts]
        # result = ""
        for l in left_dependencies:
          # 感觉要改成if l.text.lower() in UNITS or l.like_num:，
          # 如果在左侧依赖中找到数字类似的词汇，将其也存储到self.time中
          if(l.lower in UNITS or l.like_num):
            self.time = [l, token]
            # 返回找到的数词和时间词的索引
            return {l.i, token.i}
    return None

  
  def set_rest(self, indices):
    time = self.set_time()
    if(time is not None):
      for j in time:
        indices.add(j)
    result = list()
    for token in self.clause:
      if(token.i in indices):
        continue
      result.append(token)
    if(result):
      self.rest = result

  def clause_as_string(self):
    return ''.join(s.text_with_ws for s in self.clause)
   
  def clause_as_lemmatized_list(self):
    result = list()
    for word in self.clause:    
      if(word.lemma_ == "PRON"):
        result.append(word.text)
      else:
        if(word.is_punct or word.like_num or word.is_space or word.text in self.stopwords):
          continue
        result.append(word.lemma_)
    return result 
    
  def clause_as_lemmatized_string(self):
    return " ".join(self.clause_as_lemmatized_list()) 
   
  def subject_as_string(self):
    if(self.subject is None):
      return "\nNO SUBJECT"
    return ''.join(s.text_with_ws for s in self.subject)

  def verb_as_string(self):
    if(self.verb is None):
      return "\nNO VERB"
    return ''.join(s.text_with_ws for s in self.verb)
      
  def object_as_string(self):
    if(self.object is None):
      return "\nNO OBJECT"
    return ''.join(s.text_with_ws for s in self.object)
    
  def rest_as_string(self):
    if(self.rest is None):
      return "\nNO REST"
    return ''.join(s.text_with_ws for s in self.rest)


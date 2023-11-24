## Flow = Sequential Order Relation
from .Clause import *

class Flow:
  def __init__(self, _id, condition, consequence, stopwords):
    self._id = _id
    self.condition = condition
    self.consequence = consequence
    self.stopwords = stopwords
    
  def __repr__(self):
    return "1: " + ''.join(s.text_with_ws for s in self.condition) + "\n2: " + ''.join(s.text_with_ws for s in self.consequence) + "\n" 
    
  def lemmatize_condition(self):
    result = list()
    if(isinstance(self.condition, Clause)):
      for word in self.condition.clause:
        if(word.lemma_ == "PRON"):
          result.append(word.text)
        else:
          if(word.is_punct or word.like_num or word.is_space or word.text in self.stopwords):
            continue
          result.append(word.lemma_)
      return " ".join(result)
    for word in self.condition:    
      if(word.lemma_ == "PRON"):
        result.append(word.text)
      else:
        if(word.is_punct or word.like_num or word.is_space or word.text in self.stopwords):
          continue
        result.append(word.lemma_)
    return " ".join(result)
    
  def lemmatize_consequence(self):
    result = list()
    if(isinstance(self.consequence, Clause)):
      for word in self.consequence.clause:
        if(word.lemma_ == "PRON"):
          result.append(word.text)
        else:
          if(word.is_punct or word.like_num or word.is_space or word.text in self.stopwords):
            continue
          result.append(word.lemma_)
      return " ".join(result)
    for word in self.consequence:    
      if(word.lemma_ == "PRON"):
        result.append(word.text)
      else:
        if(word.is_punct or word.like_num or word.is_space or word.text in self.stopwords):
          continue
        result.append(word.lemma_)
    return " ".join(result)
      

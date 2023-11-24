import collections
from .Sentence import *
from .Paragraph import *
from .functions import test_constraint

class Document_Collection:
  def __init__(self, _id, paragraphsraw, signalwords, sequencemarkers, stopwords, nlp, only_constraints):
    self._id = _id
    self.paragraphsraw = paragraphsraw
    self.signalwords = signalwords
    self.sequencemarkers = sequencemarkers
    self.stopwords = stopwords
    self.nlp = nlp
    self.only_constraints = only_constraints
    self.constraints = list()
    self.paragraphs = self.get_paragraphs()


### calculate paragraphs and build sentences and clauses
  def get_paragraphs(self):
    paras = list()
  
    for paraid, para in self.paragraphsraw.items():
      result = list()
      doc = self.nlp(para)
      doc.user_data["id"] = paraid 
        
      sentences = doc.sents  ## 拆分句子
    
      for idx, sentence in enumerate(sentences):    
        flag = test_constraint(sentence, self.signalwords) ##调用 test_constraint 函数，用于检查句子中是否包含了约束条件（信号词）
        sentence_object = Sentence(doc.user_data["id"], doc.user_data["id"]+str(idx), self.nlp, self.stopwords, flag, sentence)
        ## 根据sentence、段落标识符和其他参数创建一个 Sentence 对象，并将其存储在 sentence_object 变量中。
        result.append(sentence_object)
        if(flag):
          self.constraints.append(sentence_object) ##将包含约束条件的句子对象添加到 self.constraints 列表中
      paras.append(Paragraph(doc.user_data["id"], result, self.sequencemarkers, self.only_constraints))
      ## 创建一个 Paragraph 对象，将段落标识符、句子分析结果 result、sequencemarkers 传递给 Paragraph 构造函数，并将 Paragraph 对象添加到 paras 列表中
    return paras


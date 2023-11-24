from collections import defaultdict
from .Flow import *

class Paragraph:
  def __init__(self, paragraphID, sentences, sequencemarkers, only_constraints):
    self.paragraphID = paragraphID
    self.sentences = sentences
    self.sequencemarkers = sequencemarkers
    self.only_constraints = only_constraints
    self.obligations = self.calculate_obligations()
    self.flows = self.calculate_flows()   # flow = sequential order relation
    
  def __repr__(self):
    result = "id: %s\n" % (self.paragraphID) + "\n"
    for s in self.sentences:
      result += repr(s) + "\n"
    return result

  # take all clauses in lemmatized bag-of-words representation
  # 把所有含信号词的句子里的子句放到obligation中（若没有子句将整个句子放入）
  def calculate_obligations(self):
    result = list()
    for sentence in self.sentences:
      # 表示只关注包含约束的句子
      if(self.only_constraints):
        if(sentence.constraint is False):
          continue
        for clause in sentence.clauses:
          result.append(clause) 
        if(not result):
          result.append(self.sentences)
      else:
        for clause in sentence.clauses:
          result.append(clause) 
        if(not result):
          result.append(self.sentences)
    return result

  ## CALCULATE FLOWS ############### START
  def calculate_flows(self):
    # 检查是否只有一个义务
    if(len(self.obligations) == 1):
      # 如果是，则返回 None，因为不能构建流程关系。
      return None
    result = list()
    #遍历所有约束
    for idx, obligation in enumerate(self.obligations):
      #判断义务句内部是否存在流程关系
      if(self.exists_flow_intra(obligation)):
        tmp = self.extract_intra_flow(obligation)
        # 返回一个流对象，将义务的id，条件，结果和stopwords传入
        result.append(Flow(obligation._id, tmp[0], tmp[1], obligation.stopwords))
      #此处代码逻辑错误，应该是判断当前义务是否与段内其他义务之间有流关系，但是传进去的两个参数皆为自身
      elif (self.exists_flow(obligation, self.obligations[idx])):
        result.append(Flow(obligation._id, obligation, self.obligations[idx], obligation.stopwords))
    return result

  def exists_flow_intra(self, obligation):
    for x in obligation.clause:
      # 判断义务句首词是不是After（这边写的非常奇怪）
      if(x.text in self.sequencemarkers and x.i == 0 and x.text == "After"):
        return True
    return False
        
  def extract_intra_flow(self, obligation):
    condition = list()
    consequence = list()
    indices = list()
    # 遍历义务从句第一个词（After）的子树，逐个添加作为condition
    for t in obligation.clause[0].subtree:
      condition.append(t)
      indices.append(t.i)
    # 将不属于因的作为果
    for t in obligation.clause:
      if(t.i not in indices):
        consequence.append(t)
    return (condition, consequence)

  def exists_flow(self, obl1, obl2):
    for x in obl1.clause:
      if(x.text in self.sequencemarkers and x.i !=0):
        return True
    return False
  ## CALCULATE FLOWS ############### END    

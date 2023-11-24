from .Clause import *

from .functions import subtrees, sort_clauses, contains_verb

SUBJECTS = ["nsubj", "nsubjpass", "csubj", "csubjpass", "agent", "expl"]
COMP = ["compound", "amod", "conj"]

class Sentence:
  def __init__(self, paragraphID, _id, nlp, stopwords, constraint, original): 
    self.paragraphID = paragraphID
    self._id = _id
    self.nlp = nlp
    self.stopwords = stopwords
    self.constraint = constraint
    self.original = original.as_doc()
    self.clauses = self.calculate_clauses()

    
  def __repr__(self):
    s = "ORIGINAL: " + self.original.text + "\n"
    for cl in self.clauses:
      s += repr(cl) + "\n\n"  
    return s
    
  def __str__(self):
    s = "ORIGINAL: " + self.original.text + "\n"
    for cl in self.clauses:
      s += repr(cl) + "\n\n"  
    return s
  
  def __add__(self, other):
    return str(self) + other
  
  def __radd__(self, other):
    return other + str(self)
    
        
  def calculate_clauses(self):
    for word in self.original:
      if(word.dep_ == 'ROOT'):
        root = word
    # 递归得到一个子树列表tree，列表中的每个元素为一个元组（树根，子树）
    trees = subtrees(root)
    curr = list() # 记录以及处理过的元素
    clauses = list()
    for idx, t in enumerate(reversed(trees)):  #从底向上遍历所有子树
      # 如果子树的根词的依赖关系为'ROOT'，或者它的依赖关系为'conj'并且词性为'VERB'，或者根词具有依存关系"prep"并且它的子树（t[1]）包含动词。
      if(t[0].dep_ == "ROOT" or (t[0].dep_ == 'conj' and t[0].pos_ == "VERB") or (t[0].dep_ == 'prep' and contains_verb(t[1]))):
        # 把未处理过的子句，子句id传入，构造一个从句对象添加到clauses列表
        clauses.append(Clause(self._id + str(idx), self.nlp, self.stopwords, [i for i in t[1] if not i in curr]))
        curr.extend(t[1])
    # 按照子句中第一个词的索引排序
    clauses.sort(key = sort_clauses)
    #subject cannot be set within clause as it might be that we need the subject of the previous clause -> anaphora resolution
    previous_subj = None
    for clause in clauses:   
      for token in clause.clause:
        # 如果该词语的依赖关系在 SUBJECTS 中，并且其父词性为'VERB'且该词不是代词（'PRON'），则表示找到了主语。
        if(token.dep_ in SUBJECTS and token.head.pos_ == 'VERB' and token.pos_ != "PRON"):
          # "agent" 通常表示执行动作的主体，用于描述动作的执行者。
          if(token.dep_ == "agent"):
            # 从与当前词语的同一子树中的所有词语中筛选出在当前词语左侧并且依赖关系为comp的词语作为子句的主语。
            previous_subj = [t for t in token.subtree if ((t.dep_ in COMP and t in token.lefts) or t == token)]
          else:
            previous_subj = [t for t in token.subtree if ((t.dep_ in COMP and t in token.lefts) or t == token)]
      clause.set_subject(previous_subj)
      # set remaining elements -> needed for cost_score
      clause.set_remaining()
    return clauses  
 

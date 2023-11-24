# from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
import spacy
import re
from .Mapping import *

class Pair:
  def __init__(self, nlp, sim, model, paragraph, resource_set, gamma, delta):
    self.nlp = nlp
    self.sim = sim
    self.model = model
    self.paragraph = paragraph
    self.resource_set = resource_set
    self.gamma = gamma
    self.delta = delta
    self.mapping = self.calculate_mapping()     
    self.fitness = self.fitness_score() 
    self.cost_obligation = self.cost_obligation(self.gamma)   
    self.cost_resource = self.cost_resource(self.gamma, self.delta)
    self.cost_so = self.cost_so(self.gamma)    
    self.cost = self.cost_score(float(1)/3, float(1)/3, float(1)/3)   # parameters = w_o, w_a, w_so
     
  def __repr__(self):
    return "Model ID: " + str(self.model._id) + "\nParagraph ID: " + str(self.paragraph.paragraphID) + "\nFitness:  " + str(round(self.fitness,5)) + "\nCost: " + str(round(self.cost,5))
    
    
## CALCULATE MAXIMAL OBLIGATION PAIRS ############################## START
  def calculate_mapping(self):
    model_obligations = self.model.obligations
    model_obligations_lemmatized = self.model.lemmatized_obligations
    paragraph_obligations = self.paragraph.obligations
    mapping = list()
    for para_obligation in paragraph_obligations:
      max_element = self._max_text_obligation_to_model(para_obligation, model_obligations, model_obligations_lemmatized)
      mapping.append(Mapping(para_obligation, para_obligation.lemmatized, max_element[0], max_element[1], max_element[2], max_element[3], max_element[4]))   #[0] = model_obligation, [1] = lemmatized_model_obligation, [2] = resource of maxelement, [3] = score
    return mapping
  
  def _max_text_obligation_to_model(self, text_obligation, model_obligations, model_obligations_lemmatized):
    max_score = 0
    max_element = None
    first = True
    for key in model_obligations_lemmatized.keys():
      # resource_obligations是模型义务的标签词元化后的list
      resource_obligations = model_obligations_lemmatized[key] # list of obligatory tasks for an resource
      for idx, model_obligation in enumerate(resource_obligations):
        if(first):
          max_element = model_obligations[key][idx]
          max_element_lemmatized = model_obligations_lemmatized
          proc = model_obligations[key]
          resource = key
        sim_score = self.sim.spacy_similarity_text_model_obligation(text_obligation.lemmatized, model_obligation)
        if(sim_score > max_score):      
          max_score = sim_score
          max_element = model_obligations[key][idx]
          max_element_lemmatized = model_obligations_lemmatized
          proc = model_obligations[key]
          resource = key
    # 返回（义务dom元素，假的义务词元化 ，参与者，分数，整个参与者的约束列表）
    return (max_element, max_element_lemmatized, resource, max_score, proc)
## CALCULATE MAXIMAL OBLIGATION PAIRS ############################## END

###########################################################
## FITNESS SCORE ############################## START
###########################################################
  def fitness_score(self):
    sum_scores = 0
    sum_all = 0
    for mapping in self.mapping:
      if(mapping.sim_score > self.gamma):
        sum_scores += mapping.sim_score
        sum_all += 1
    if(sum_all == 0):
      return 0
    return float(sum_scores)/sum_all
###########################################################
## FITNESS SCORE ############################## END
###########################################################


###########################################################
## COST SCORE ############################## START
###########################################################
  def cost_score(self, w_obligation, w_resource, w_so):
    return w_obligation*self.cost_obligation + w_resource*self.cost_resource + w_so*self.cost_so 
  
################################################################  
  # OBLIGATION COSTS ################ START
  # 违规1
  def cost_obligation(self,gamma):
    count_violations = 0
    count_all = 0
    for mapping in self.mapping:
      count_all += 1
      if(mapping.sim_score < gamma):
        count_violations += 1
    if(count_all == 0):
      return 0
    return float(count_violations)/count_all
  # OBLIGATION COSTS ################ START 
################################################################
  
################################################################  
  # RESOURCE COSTS ################ START
  # 参与者错误违规
  def cost_resource(self, gamma, gamma_resource):
    if(not self.resource_set):
      return 0
    count_violations = 0
    count_all = 0
    for mapping in self.mapping:
      count_all += 1
      if(self.check_resource_violation(mapping, gamma, gamma_resource)):
        count_violations += 1
    if(count_all == 0):
      return 0
    return float(count_violations)/count_all
  
  def check_resource_violation(self, mapping, gamma, gamma_resource):
    if(self.sim.spacy_similarity_task_clause(mapping.model_obligation_lemmatized, mapping.paragraph_obligation) > gamma):
      for a in self.resource_set:
        # 如果资源在段落义务的词元里，该资源和模型资源之间的相似度小于delta并且模型资源不在段落义务的词元则判断产生了参与者违规
        if(a.lower() in mapping.paragraph_obligation_lemmatized
                and self.nlp(a.lower()).similarity(self.nlp(mapping.model_resource.lower())) < gamma_resource
                and mapping.model_resource.lower() not in mapping.paragraph_obligation_lemmatized):
         return True
    return False
  # RESOURCE COSTS ################ END  
################################################################
 
################################################################  
  # FLOW COSTS ################ START    
  def cost_so(self, gamma):
    paragraph_flows = self.paragraph.flows
    if(paragraph_flows is None):
      return 0
    count_violations = 0
    count_all = 0
    for para_flow in paragraph_flows:
      # 将段落中的所有流都作为分母
      count_all += 1
      for m in self.mapping:
        # 枚举mapping中的段落义务，找到同para_flow的义务id相同的
        if(para_flow._id == m.paragraph_obligation._id):
          for x in self.model.processes:
            if(x.participant == m.model_resource):
              process_object = x
              # process_object 完全没用到
          if(self.check_flow_violation(para_flow, m, process_object, gamma)):
            count_violations += 1
    if(count_all == 0):
      return 0
    return float(count_violations)/count_all
    
  def check_flow_violation(self, para_flow, mapping, process_object, gamma):

    if(self.nlp(para_flow.lemmatize_condition()).similarity(self.nlp(" ".join(mapping.model_obligation_lemmatized))) > gamma):
      regexp = re.compile(r'.+')  # 表示检测名字非空
      obligation_id = mapping.model_obligation.getAttribute("id")
      for compare in mapping.process:
        c = compare.getAttribute("name")
        if regexp.search(c):
          compare_label = c    
        else:
          continue
        compare_id = compare.getAttribute("id")
        # 如果1.此事件的name和para_flow的cons相似度大于阈值 2.此事件的name和模型的不同 3.顺序无误（可以从前到后，不能从后道歉）
        if (self.nlp(compare_label).similarity(self.nlp(para_flow.lemmatize_consequence())) > gamma
                and compare_label != " ".join(mapping.model_obligation_lemmatized)
                and process_object.is_reachable_from(obligation_id, compare_id)
                and not process_object.is_reachable_from(compare_id, obligation_id)):
          return True
      return False
    return True
  # FLOW COSTS ################ END
################################################################

class BPMN:
  def __init__(self, _id, processes):
    self._id = _id
    self.processes = processes
    self.obligations = self.model_as_obligation_list()
    self.lemmatized_obligations = self.model_as_lemmatized_obligation_list()
    self.flows = self.calculate_flows()


  def __repr__(self):
    return "FileID: " + self._id + ", Processes: " + repr(self.processes)
  
  def model_as_obligation_list(self):
    result = dict()
    for p in self.processes:
      result[p.participant] = p.obligation_list
    return result
    
  def model_as_lemmatized_obligation_list(self):
    result = dict()
    for p in self.processes:
      result[p.participant] = p.obligation_list_labels_lemmatized
    return result
    
  def calculate_flows(self):
    result = dict()
    for p in self.processes:
      result[p.participant] = p.flows
    return result

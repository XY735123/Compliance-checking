class Mapping:
  def __init__(self, paragraph_obligation,paragraph_obligation_lemmatized, model_obligation,model_obligation_lemmatized, model_resource, sim_score, process):
    self.paragraph_obligation = paragraph_obligation 
    self.paragraph_obligation_lemmatized = paragraph_obligation_lemmatized   
    self.model_obligation = model_obligation
    self.model_obligation_lemmatized = model_obligation_lemmatized
    self.model_resource = model_resource
    self.sim_score = sim_score
    self.process = process
    
  def __repr__(self):
    return "\n---------------------\nParagraph: " + self.paragraph_obligation + "\n\nModel: " + " ".join(self.model_obligation_lemmatized) + "Resource:" + self.model_resource + "\n\n------------------------------"

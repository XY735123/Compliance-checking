import csv

## function for finding constraints ########################## 
def test_constraint(sentence, signalwords):
  for word in sentence:
    if(word.text in signalwords):
      return True
  return False


## find subtrees in Sentence recursively ########################## 
def subtrees(node):
  if not node.children:
    return []
  result = [ (node, list(node.subtree)) ]
  for child in node.children:
    result.extend(subtrees(child))
  return result


def sort_clauses(val):
  if len(val.clause) == 1:
    return 1
  return val.clause[0].i

  
def contains_verb(t):
  for word in t:
    if(word.pos_ == "VERB"):
      return True
  return False


def sort_by_paragraphID(val):
  return val.paragraph.paragraphID    

def evaluation_csv(targetdir, pairs_per_model):
  for k, v in pairs_per_model.items():
    fieldnames = list()
    fielddicts = list()
    v.sort(key = sort_by_paragraphID)
    fieldnames.append("paragraphs")
    fieldnames.append("fitness score")
    fieldnames.append("obligation costs")
    fieldnames.append("so costs")
    fieldnames.append("resource costs")
    fieldnames.append("costs")
    for x in v:
      fielddict = dict()
      fielddict["paragraphs"] = x.paragraph.paragraphID 
      fielddict["fitness score"] = round(x.fitness,5) 
      fielddict["obligation costs"] = round(x.cost_obligation,5) 
      fielddict["so costs"] = round(x.cost_so,5)
      fielddict["resource costs"] = round(x.cost_resource,5) 
      fielddict["costs"] = round(x.cost,5)
      fielddicts.append(fielddict)
    with open(targetdir+'results_'+k+'.csv', mode = 'w') as f:
      writer = csv.DictWriter(f, fieldnames=fieldnames)
      writer.writeheader()
      for d in fielddicts:
        writer.writerow(d)     

# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
import spacy
import json
import os

class SimilarityComputer:
    def __init__(self, nlp, bpmn_models, document_collection, stopwords, spacy_cache):
        # self.document_collection = document_collection
        # self.bpmn_models = bpmn_models
        self.nlp = nlp
        self.stopwords = stopwords
        self.spacy_cache = spacy_cache
        self.load_spacy_sim_cache()

    def load_spacy_sim_cache(self):
        # 加载之前计算的相似性计算结果的缓存。
        if os.path.exists(self.spacy_cache):
            with open(self.spacy_cache, 'r') as f:
                self.spacy_dict = json.load(f)
        else:
            self.spacy_dict = {}
        print("loaded", len(self.spacy_dict), "spacy sim values")

    def spacy_similarity(self, model, paragraph):
        # check if sim value in cache
        key = self._model_par_to_key(model, paragraph)
        if key in self.spacy_dict:
            return self.spacy_dict[key]

        # else, compute and store value
        model_lemma = self.nlp(model.get_lemmatized_obligation_list())
        para_lemma = self.nlp(paragraph.lemmatize_string())
        sim_val = model_lemma.similarity(para_lemma)
        self.spacy_dict[key] = sim_val
        return sim_val

    def dump_spacy_cache(self):
        print("dumping spacy similarity values to", self.spacy_cache)
        with open(self.spacy_cache, 'w') as fp:
            json.dump(self.spacy_dict, fp)

    def _model_par_to_key(self, model, paragraph):
        return model._id + "__model_par_to_key___" + paragraph.paragraphID
        

    def spacy_similarity_task_clause(self, task, clause):
        # check if sim value in cache
        key = self._task_clause_to_key(task, clause)
        if key in self.spacy_dict:
            return self.spacy_dict[key]

        # else, compute and store value
        task_lemma = self.nlp(" ".join(task))
        clause_lemma = self.nlp(clause.lemmatized)
        if(task_lemma.has_vector is False or clause_lemma.has_vector is False):
          self.spacy_dict[key] = 0
          return 0
        sim_val = task_lemma.similarity(clause_lemma)
        self.spacy_dict[key] = sim_val
        return sim_val

    def spacy_similarity_text_model_obligation(self, text_obligation, model_obligation):
        # check if sim value in cache
        key = self._text_model_obligation_to_key(text_obligation, model_obligation)
        if key in self.spacy_dict:
            return self.spacy_dict[key]

        # else, compute and store value
        model_lemma = self.nlp(" ".join(model_obligation))
        para_lemma = self.nlp(text_obligation)
        if(model_lemma.has_vector is False or para_lemma.has_vector is False):
          self.spacy_dict[key] = 0
          return 0
        sim_val = para_lemma.similarity(model_lemma)
        self.spacy_dict[key] = sim_val
        return sim_val

    def _text_model_obligation_to_key(self, text_obligation, model_obligation):
        return "".join(text_obligation) + "___text_model_obligation_to_key___" + "".join(model_obligation)

    def _task_clause_to_key(self, task, clause):
        return "".join(task) + "__task_clause_to_key___" + clause._id

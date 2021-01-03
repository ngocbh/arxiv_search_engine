import os, sys
import spacy
import nltk
import lemminflect
import copy
import string
import re

from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import brown
from spacy.lemmatizer import Lemmatizer
from spacy.lookups import Lookups
# nltk.download('brown')
# word_set = set(brown.words())

nlp = spacy.load("en_core_web_sm")
ps = PorterStemmer()

def preprocess_text(text):
    text = text.replace('\n', ' ').strip()
    # my_words = word_tokenize(text)
    # for word in my_words:
    #     if '-' in word:
    #         tokens = word.split('-')
    #         for token in tokens:
    #             if token.lower() not in word_set and word.replace('-','').lower() in word_set:
    #                 text = text.replace(word, word.replace('-', ''))
    #                 break
    return text

def find_subjects(sent, deps):
    ret = []

    def dependency_tree(node, deps, ret):
        if node.dep_ in deps:
            ret.append(node.subtree)
            return

        for child in node.children:
            dependency_tree(child, deps, ret)

    dependency_tree(sent.root, deps, ret) 
    return ret

def parse_sent(text, subtree=True):
    doc = nlp(text)

    records = []
    for chunk in doc.noun_chunks:
        subj_tokens = [token for token in (chunk.subtree if subtree else chunk)]

        record = {}
        start_idx = subj_tokens[0].idx 
        end_idx = subj_tokens[-1].idx + len(subj_tokens[-1].text)
        record['origin'] = text[start_idx:end_idx]
        record['lemma'] = ' '.join([ps.stem(token.text.strip().lower()) for token in subj_tokens if not token.is_punct])
        record['dep'] = chunk.root.dep_
        if record['dep'] in ['nsubj', 'nsubjpass', 'pobj', 'dobj']:
            records.append(record)
    return records

def match_phrase(text, phrase, subjs, deps=['nsubj', 'nsubjpass'], is_head=False, is_tail=False):
    phrase = phrase.translate(str.maketrans('', '', string.punctuation))
    phrase_lemma = ' '.join([ps.stem(token.strip().lower()) for token in phrase.split()])

    presence = False
    highlighted_sent_text = copy.deepcopy(text)

    for subj in subjs:
        if subj['dep'] in deps and phrase_lemma in subj['lemma']:
            highlighted_sent_text = highlighted_sent_text.replace(subj['origin'], "<em>{}</em>".format(subj['origin']), 1) 
            presence = True

    if presence:
        if is_head:
            highlighted_sent_text = '...' + highlighted_sent_text
        if is_tail:
            highlighted_sent_text = highlighted_sent_text + '...'
        return highlighted_sent_text
    else:
        return None



if __name__ == "__main__":
    doc = """
The first component of this proposed system is a web based interface or Graphical User Interface, which resides on top of the Client Application Program, the second component of the system is a client Application program running in an application server, which resides on top of the Global Database Management System, the third component of the system is a Global Database Management System and global schema of the multidatabase system server, which resides on top of the distributed heterogeneous local component database system servers, and the fourth component is remote heterogeneous local component database system servers
    """
    print(parse_sent(doc, True))


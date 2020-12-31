import os, sys
import spacy
import nltk
import lemminflect
import copy

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


def match_phrase(text, phrase, deps=['nsubj', 'nsubjpass'], subtree=True):
    phrase_doc = nlp(phrase)
    phrase_lemma = ' '.join([ps.stem(token.text.strip().lower()) for token in phrase_doc if not token.is_punct])

    ret = []
    text = preprocess_text(text)
    doc = nlp(text)
    sents = [sent for sent in doc.sents]

    for i, sent in enumerate(sents):
        presence = False
        sent_text = sent.text
        highlighted_sent_text = copy.deepcopy(sent_text)

        for chunk in sent.noun_chunks:
            subj_tokens = [token for token in (chunk.subtree if subtree else chunk)]

            start_idx = subj_tokens[0].idx - sent[0].idx
            end_idx = subj_tokens[-1].idx + len(subj_tokens[-1].text) - sent[0].idx
            subj_origin = sent_text[start_idx:end_idx]
            subj_lemma = ' '.join([ps.stem(token.text.strip().lower()) for token in subj_tokens if not token.is_punct])
            subj_dep = chunk.root.dep_

            if subj_dep in deps and phrase_lemma in subj_lemma:
                highlighted_sent_text = highlighted_sent_text.replace(subj_origin, "<em>{}</em>".format(subj_origin), 1) 
                presence = True

        if presence:
            if i != 0:
                highlighted_sent_text = '...' + highlighted_sent_text
            if i != len(sents) - 1:
                highlighted_sent_text = highlighted_sent_text + '...'
            ret.append(highlighted_sent_text)

    return ret


if __name__ == "__main__":
    doc = """
The first component of this proposed system is a web based interface or Graphical User Interface, which resides on top of the Client Application Program, the second component of the system is a client Application program running in an application server, which resides on top of the Global Database Management System, the third component of the system is a Global Database Management System and global schema of the multidatabase system server, which resides on top of the distributed heterogeneous local component database system servers, and the fourth component is remote heterogeneous local component database system servers
    """
    print(match_phrase(doc, 'system'))


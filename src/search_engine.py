from elasticsearch import Elasticsearch
from pos_tagger import match_phrase, find_subjects 

import json
import time
import utils
from tqdm import tqdm

es = Elasticsearch()

def delete_dataset(index):
    es.indices.delete(index=index, ignore=404)


def put_configuration(index):
    settings = utils.load_es_settings()
    es.indices.create(index=index, body=settings)
    
def index_dataset(index, datapath, reindex=False):
    if not es.indices.exists(index=index) or reindex:
        if reindex:
            delete_dataset(index)
        
        put_configuration(index)
        print("Indexing dataset. It will take a while... ")
        with open(datapath, encoding='utf-8', mode='r') as f:
            data = f.read()
            es.bulk(index=index, body=data, request_timeout=10000)

    print("Indexed")

def query_database(field, phrase, index, _size=100, _from=0):
    query = {
        'from': _from,
        'size': _size,
        'query': {
            'match_phrase': {
                field: {
                    "query": phrase,
                    "analyzer": "english_exact"
                }
            }
        },
    }
    res = es.search(index=index, body=query)
    return res

def search_phrase(phrase, field, index, _size=100, _from=0, deps=['nsubj', 'nsubjpass'], subtree=True):
    res = query_database(field, phrase, _size=_size, _from=_from, index=index)
    ret = {'records': []}
    # print(res)
    start_time = time.time()
    no_papers = len(res['hits']['hits'])
    for hit in res['hits']['hits']:
        field_data = hit['_source'][field]
        sents = match_phrase(field_data, phrase, deps, subtree)
        
        for sent in sents:
            record = {}
            record['sentence'] = sent
            record['paper_id'] = hit['_source']['id']
            record['authors'] = utils.shorten_author(hit['_source']['authors'])
            record['title'] = utils.shorten_title(hit['_source']['title'])
            record['date'] = utils.shorten_date(hit['_source']['update_date'])
            ret['records'].append(record)
    ret['no_hits'] = res['hits']['total']['value']
    ret['se_time'] = res['took']
    ret['nlp_time'] = round((time.time() - start_time) * 1000)
    ret['no_papers'] = no_papers
    return ret


if __name__ == '__main__':
    # index_dataset()
    keywords = 'data structure'
    # ret = search_phrase(keywords, _size=1000)
    # print(ret)
    # print(res)
    # print("Got %d Hits:" % res['hits']['total']['value'])
    # print(len(res['hits']['hits']))
    # for hit in res['hits']['hits']:
    #     print("Title=%(title)s\n\n Author=%(authors)s\n\n Abstract=%(abstract)s\n\n\n" % hit["_source"])

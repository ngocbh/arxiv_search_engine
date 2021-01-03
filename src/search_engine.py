from elasticsearch import Elasticsearch
from pos_tagger import match_phrase, find_subjects, parse_sent 

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
    cluster_settings = { "transient": { "cluster.routing.allocation.disk.threshold_enabled": False } }
    es.cluster.put_settings(body=cluster_settings)

    
def index_dataset(index, datapath, reindex=False):

    if not es.indices.exists(index=index) or reindex:
        if reindex:
            delete_dataset(index)
        
        put_configuration(index)
        print(f"Indexing {index}. It will take a while... ")
        with open(datapath, encoding='utf-8', mode='r') as f:
            data = f.read()
            es.bulk(index=index, body=data, request_timeout=10000)

    print("Indexed")

def query_sentences(field, phrase, index, _size=100, _from=0):
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

def search_phrase(phrase, field, abstract_index, title_index, _size=100, _from=0, deps=['nsubj', 'nsubjpass'], subtree=True):
    res = query_sentences(field, phrase, _size=_size, _from=_from, index=abstract_index)
    ret = {'records': [], 'se_time': 0, 'nlp_time': 0}
    # print(res)
    no_papers = len(res['hits']['hits'])
    index_subjs = ''

    for hit in res['hits']['hits']:
        field_data = hit['_source'][field]

        subjs_key = 'subjs_{}'.format(1 if subtree else 0)
        start_time = time.time()
        if subjs_key not in hit['_source'] or hit['_source'][subjs_key] == '':
            subjs = parse_sent(field_data, subtree)
            index_post = {"update": {"_index": abstract_index, "_id": hit['_id']}}
            index_subjs += json.dumps(index_post) + '\n'
            index_subjs += json.dumps({"doc": {subjs_key: json.dumps(subjs)}}) + '\n' 
        else:
            subjs = json.loads(hit['_source'][subjs_key])
        highlighted_sent_text = match_phrase(field_data, phrase, subjs, 
                                             deps, is_head=hit['_source']['head'], 
                                             is_tail=hit['_source']['tail'])
        ret['nlp_time'] += round((time.time() - start_time) * 1000)
        
        if highlighted_sent_text is not None:
            metadata = es.get(index=title_index, id=hit['_source']['paper_id'])
            record = {}
            record['sentence'] = highlighted_sent_text
            record['paper_id'] = hit['_source']['id']
            record['authors'] = utils.shorten_author(metadata['_source']['authors'])
            record['title'] = utils.shorten_title(metadata['_source']['title'])
            record['date'] = utils.shorten_date(metadata['_source']['update_date'])
            ret['records'].append(record)

    if index_subjs != '':
        es.bulk(index=abstract_index, body=index_subjs, request_timeout=10)

    ret['no_hits'] = res['hits']['total']['value']
    ret['se_time'] += res['took']
    ret['no_papers'] = no_papers
    return ret


if __name__ == '__main__':
    # index_dataset()
    # keywords = 'data structure'
    # ret = search_phrase(keywords, 'sent', 'abstract_arxiv_dataset_50k', 'title_arxiv_dataset_50k', _size=10)
    # print(ret)
    # delete_dataset(index='abstract_arxiv_dataset_500k')
    # delete_dataset(index='abstract_arxiv_dataset_50k')
    # delete_dataset(index='title_arxiv_dataset_500k')
    # delete_dataset(index='title_arxiv_dataset_50k')
    # print(res)
    # print("Got %d Hits:" % res['hits']['total']['value'])
    # print(len(res['hits']['hits']))
    # for hit in res['hits']['hits']:
    #     print("Title=%(title)s\n\n Author=%(authors)s\n\n Abstract=%(abstract)s\n\n\n" % hit["_source"])
    pass

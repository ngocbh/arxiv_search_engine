from flask import Flask
from flask import render_template, redirect, request, jsonify, url_for
from search_engine import index_dataset, search_phrase, query_sentences
from flask_paginate import Pagination, get_page_args

import utils
import datetime, time
import json
import codecs
import requests
import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

configs = utils.load_configs(os.path.join(__location__, 'config/config.yml'))
abstract_index = utils.get_index(configs, 'abstract_dataset')
title_index = utils.get_index(configs, 'title_dataset') 

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', title='A Simple Search Engine for arxiv dataset')

@app.route('/search')
def serp():
    query = request.args.get('q', '')
    field = request.args.get('field', 'sent')
    page = request.args.get('page', '1')
    _size = request.args.get('size', '50')
    deps = utils.get_deps(configs)
    page = int(page)
    _size = int(_size)
    print(query)
    print(deps)
    res = search_phrase(query, field=field, deps=deps, 
                        abstract_index=abstract_index, 
                        title_index=title_index,
                        _from=(page-1)*_size, 
                        _size=_size,
                        subtree=configs['parser']['subtree'])
    records = []
    for record in res['records']:
        record['sentence'] = record['sentence'].replace('<em>', '<span class="serp__match">').replace('</em>','</span>')
        records.append(record)
    no_records = len(records)
    pagination = Pagination(page=page, per_page=_size, total=res['no_hits'],
                                css_framework='bootstrap3')
    return render_template('serp.html', 
                           query=query,
                           records=records,
                           no_records=no_records,
                           no_hits=res['no_hits'],
                           se_time=res['se_time'],
                           nlp_time=res['nlp_time'],
                           no_papers=res['no_papers'],
                           page=page,
                           size=_size,
                           pagination=pagination,
                           settings=configs)

@app.route('/elasticsearch')
def elasticsearch():
    is_redirect = request.args.get('redirect', '0')
    print(is_redirect)
    if is_redirect == '1':
        url = request.referrer
        url = url.replace('/search', '/elasticsearch').replace('is_redirect=1', '')
        return redirect(url)

    query = request.args.get('q', '')
    field = request.args.get('field', 'sent')
    page = request.args.get('page', '1')
    _size = request.args.get('size', '50')
    page = int(page)
    _size = int(_size)
    res = query_sentences(field, query, index=abstract_index, _size=_size, _from=(page-1)*_size)
    return jsonify(res)

@app.route('/settings')
def settings():
    highlight = request.args.get('highlight', 'subtree')
    nouns = {}
    nouns['nsubj'] = request.args.get('nsubj', '0')
    nouns['nsubjpass'] = request.args.get('nsubjpass', '0')
    nouns['pobj'] = request.args.get('pobj', '0')
    nouns['dobj'] = request.args.get('dobj', '0')
    for key, value in nouns.items():
        nouns[key] = True if value == '1' else False

    utils.update_config(configs, (highlight=='subtree'), nouns) 
    return redirect(request.referrer)

if __name__ == '__main__':
    index_dataset(abstract_index, configs['abstract_dataset'], configs['search_engine']['reindex'])
    index_dataset(title_index, configs['title_dataset'], configs['search_engine']['reindex'])

    app.run(host='0.0.0.0', port=8080, debug=True, threaded=True)

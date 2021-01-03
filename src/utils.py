import os
import datetime
import string
import yaml
import json

from yaml import Loader

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

def shorten_author(authors):
    author_list = [author.strip() for author in authors.split(',')]
    author0 = author_list[0]
    author0 = author0.translate(str.maketrans('', '', string.punctuation))
    author0 = [x.strip() for x in author0.split(' ') if x != '']
    for i, x in enumerate(author0):
        if i != len(author0) - 1:
            if x[0].isupper():
                author0[i] = x[0] + '.'
            else:
                author0[i] = ''
    if len(author_list) > 1:
        return ' '.join(author0) + ' et al.'
    else:
        return ' '.join(author0)

def shorten_title(title, max_length=60):
    if len(title) > max_length:
        return title[:max_length-3] + '...'
    else:
        return title

def shorten_date(date, current_format="%Y-%m-%d", new_format="%Y"):
    date_time_obj = datetime.datetime.strptime(date, current_format)
    return date_time_obj.strftime(new_format)


def load_configs(config_filepath):
    config = yaml.load(open(config_filepath, mode='r'), Loader=Loader)
    return config

def update_config(configs, subtree, nouns):
    configs['parser']['subtree'] = subtree
    configs['parser']['nouns'] = nouns


def load_es_settings():
    config_filepath = os.path.join(__location__, 'config/elasticsearch_settings.json')
    with open(config_filepath, mode='r') as f:
        return json.load(f)

def get_deps(config):
    ret = []
    for key, value in config['parser']['nouns'].items():
        if value is True:
            ret.append(key)
    return ret

def get_index(config, dataset='dataset'):
    dataset = config[dataset] 
    return os.path.splitext(os.path.basename(dataset))[0]


if __name__ == '__main__':
    # load_config()
    # print(load_es_settings())
    # print(get_index({}))
    pass

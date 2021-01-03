# sse_arxiv
A Simple Search Engine for [Arxiv Datasets](https://www.kaggle.com/Cornell-University/arxiv)

Problem:
Given a keyword (e.g., “linear regression” or “deep learning”), it will find sentences (from the abstracts of papers in the dataset) whose "subjects" contain the keyword. Return the list of sentences with their subjects highlighted.


## How it looks
![alt tag](https://github.com/ngocjr7/arxiv_search_engine/blob/master/docs/demo1.png)
![alt tag](https://github.com/ngocjr7/arxiv_search_engine/blob/develop/docs/demo.png)

## How to run

### Requirements

* ```elasticsearch-7.10```: [download here](https://www.elastic.co/downloads/elasticsearch)
* ```python3.7```
```sh
pip install -r requirements.txt
```

### Run

Run ```elasticsearch```:
```sh
./bin/elasticsearch
```

Run web app:
```sh
python src/app.py
```

Check at ```https://localhost:8080```

## More data

* Download more indexed data [here](https://drive.google.com/file/d/15edMTwvfCpQwUPPrG9EbSrQgGtgbrU06/view?usp=sharing).
* Extract it to ```data``` folder.
* Update dataset config at ```src/config/config.yml```.
```
dataset: './data/arxiv_dataset_500k.json'
```
* Config ```elasticsearch``` at elasticsearch folder
> file: ```config/elasticsearch.yml```: add config: ```http.max_content_length: 1gb```

> file: ```jvm.options```: change config to: 
> ```-Xms4g -Xmx4g```





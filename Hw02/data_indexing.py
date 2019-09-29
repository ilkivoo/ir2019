from bs4 import BeautifulSoup
import re
import json
from elasticsearch import Elasticsearch
from elasticsearch.helpers import parallel_bulk
from pymystem3 import Mystem
from time import time
import glob
from datetime import datetime
import os

es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'timeout': 360, 'maxsize': 25}])
fileRelevance = f"/Users/alyokhina-o/Инфопоиск/Hw02/relevant_table_2009.xml"
fileQueries = f"/Users/alyokhina-o/Инфопоиск/Hw02/web2008_adhoc.xml"

K = 20
m = Mystem()
settings = {
    'mappings': {
        'properties': {
            'content': {
                'type': 'text'
            },
        }
    },
    'settings': {
        'analysis': {
            'analyzer': {
                'russian_complex': {
                    'tokenizer': 'word_longer_2',
                    'filter': [
                        'lowercase',
                        'russian_snow'
                    ]
                }
            },
            'tokenizer': {
                'word_longer_2': {
                    'type': 'pattern',
                    'pattern': '[a-zA-Z_0-9\u0400-\u04FF]{2,}',
                    'group': 0
                }
            },
            'filter': {
                'russian_snow': {
                    'type': 'snowball',
                    'language': 'russian'
                }
            }
        }
    }
}


def recreate_index():
    es.indices.delete(index='myandex')
    es.indices.create(index='myandex', body=settings)


def create_es_action(index, doc_id, document):
    return {
        '_index': index,
        '_id': doc_id,
        '_source': document
    }


def es_actions_generator():
    for filename in glob.glob("/Users/alyokhina-o/Инфопоиск/Hw01.02/lemmas/document*.txt"):
        with open(filename, 'r') as inf:
            doc = json.dumps({'content': inf.read()})
        doc_id = (os.path.splitext(os.path.basename(inf.name))[0])[8:]
        yield create_es_action('myandex', doc_id, doc)


def search(query, *args):
    return pretty_print_result(es.search(index='myandex', body=query, size=1000), args)
    # note that size set to 20 just because default value is 10 and we know that we have 12 docs and 10 < 12 < 20


def pretty_print_result(search_result, fields=[]):
    # fields is a list of fields names which we want to be printed
    res = search_result['hits']
    print(f'Total documents: {res["total"]["value"]}')
    data = {}
    for hit in res['hits']:
        data[hit['_id']] = 1
    return data


def get_doc_by_id(doc_id):
    return es.get(index='myandex', id=doc_id)['_source']


def get_query_ids():
    f = open(fileQueries, "rb")
    contents = f.read()
    soup = BeautifulSoup(contents, 'xml')
    queries = []
    for task in soup.find_all('task'):
        queries.append(task['id'])
    return queries


def create_query(text, flag):
    new_query = text
    if flag:
        lemmas = m.lemmatize(text)
        correct_lemmas = []
        for word in lemmas:
            match = re.search("[\s\t\n;|(){},.?!':><123456789/=+*~\[\]\"-_»“…«№`‹”‚©-]+", word)
            if not match:
                correct_lemmas.append(word)
        new_query = ' '.join(correct_lemmas)
    query = {
        'query': {
            'bool': {
                'should': [
                    {
                        'match': {
                            'content': new_query
                        }
                    }
                ]
            }
        }
    }
    return query


def get_relevance():
    relevance1 = {}
    with open(fileRelevance, 'r', encoding="cp1251") as src:
        raw_xml = src.read()
        soup = BeautifulSoup(raw_xml)

        for task in soup.find_all('task'):
            documents = task.find_all('document')
            vital = set()
            for doc in documents:
                if doc['relevance'] == 'vital':
                    vital.add(doc['id'])
            if vital:
                relevance1[task['id']] = vital
    return relevance1


def get_relevant_for_k(res, relevant, k):
    return sum([1 if doc in relevant else 0 for doc in res[:k]])


def analyze_results():
    Q = 0
    qpK, qrK, qR_average, qmapK = 0, 0, 0, 0
    qR = []
    for task_id in queries:
        results = [k for k in table[task_id]][:K]
        if task_id not in relevance:
            continue
        Q += 1
        cur_relevant = len(relevance[task_id])
        qpK += get_relevant_for_k(results, relevance[task_id], K) / K
        qrK += get_relevant_for_k(results, relevance[task_id], K) / cur_relevant
        qR.append(get_relevant_for_k(results, relevance[task_id], cur_relevant) / cur_relevant)
        qR_average += qR[-1]
        mapK = 0
        for k in range(1, K + 1):
            mapK += get_relevant_for_k(results, relevance[task_id], k) / k
        mapK /= K
        qmapK += mapK
    print(f"p@20 {qpK / Q}")
    print(f"r@20 {qrK / Q}")
    print(f"R-precision {qR_average / Q}")
    print(f"MAP@20 {qmapK / Q}")


if __name__ == "__main__":
    recreate_index()
    now = datetime.now()
    print(now)
    for ok, result in parallel_bulk(es, es_actions_generator(), queue_size=400000, thread_count=16, chunk_size=500):
        if not ok:
            print(result)
    now = datetime.now()
    print(now)
    print(es.indices.stats())
    query = {
        'query': {
            'match_all': {}
        }
    }

    print(search(query, ' '))
    f = open(fileQueries, "rb")
    contents = f.read()
    soup = BeautifulSoup(contents, 'xml')

    spend_time = 0
    table = {}
    for task in soup.find_all('task'):
        text = task.querytext.text
        timestamp = int(time())
        data = search(create_query(text), ' ')
        spend_time += int(time()) - timestamp
        table[task['id']] = data

    print(time)
    query = create_query('pda')
    print(search(create_query(text), ' '))
    relevance = get_relevance()
    queries = get_query_ids()
    analyze_results()


import time
start = time.time()
import csv
import sys
import pandas as pd
import numpy as np
from operator import itemgetter
import redis

REDIS_URL = "redis://localhost:6379/0"
r = redis.Redis(host='localhost', port=6379, db=0)

SIMILAR_COUNT = 3 #to set the number of similar words you want for each word


def read_biglist():
    biglist = pd.read_csv("big_Keywords.csv")
    bigwords = biglist.keyword.tolist()
    for token1 in bigwords:
        r.lpush("big_keywords", token1)
    

def process():
    import en_vectors_web_lg
    nlp = en_vectors_web_lg.load()

    topicdf = pd.read_csv("small_Topics.csv", encoding='Latin-1')
    topics = topicdf.Topic.tolist()

    while True:
        big_keyword = r.lpop('big_keywords').decode('utf-8')
        if not big_keyword:
            break
        key = 'keyword_score###{}'.format(big_keyword)
        for topic in topics:
            score = nlp(str(big_keyword)).similarity(nlp(str(topic)))
            elem = "{}###{}###{}".format(big_keyword, topic, score)
            r.zadd(key, {elem: score})

        n_result = r.zrevrangebyscore(key, "+inf", "-inf", start=0, num=SIMILAR_COUNT)
        result = [big_keyword] + [r.decode('utf-8').split('###')[1] for r in n_result]

        r.lpush('results', ','.join(result))
        r.delete(key)
        print(','.join(result))


def dump():
    with open('results.csv', 'w') as f:
        for key in r.lrange('results', 0, -1):
            print(key)
            f.write(key.decode('utf-8'))
            f.write('\n')


if __name__== "__main__":
    func_name = sys.argv[1]
    functions = {
        'read_biglist': read_biglist,
        'process': process,
        'dump': dump,
    }
    f = functions.get(func_name)
    f()

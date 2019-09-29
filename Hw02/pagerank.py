import numpy as np
from operator import itemgetter

graph = {}
cnt = {}


with open("result_graph.csv", 'r') as f:
    lines = f.readlines()
    for line in lines:
        arr = list(map(int, line.split()))
        if len(arr) > 1:
           graph[arr[0]] = arr[1:]
           for i in arr[1:]:
               if i not in cnt:
                   cnt[i] = 0
               cnt[i] += 1

print(len(cnt))

all_cnt = [(i, num) for i, num in cnt.items()]
all_cnt = sorted(all_cnt, key=itemgetter(1), reverse=True)
print(all_cnt[:10])
all = set()
for i in range(200):
    all.add(all_cnt[i][0])

n = len(all)
print(n)

big_to_small = {}
small_to_big = {}

sz = 0
for t in all:
    big_to_small[t] = sz
    small_to_big[sz] = t
    sz += 1


adj_matrix = np.zeros((n, n))

for v, to in graph.items():
    if v not in all:
        continue
    for u in to:
        if u not in all:
            continue
        adj_matrix[big_to_small[v]][big_to_small[u]] = 1

probs = np.zeros(adj_matrix.shape)
sigma = 0.15 / probs.shape[0]

for i in range(adj_matrix.shape[0]):
    ss = sum(adj_matrix[i])
    if ss != 0:
        probs[i] = adj_matrix[i] / ss
        if ss != adj_matrix.shape[1]:
            probs[i] *= 0.85
            probs[i] = np.array([x + sigma if (x > 0) else sigma for x in probs[i]])
    else:
        probs[i] = np.ones(probs[i].shape) / probs[i].shape


print(probs)

start = np.zeros(n).T
start[0] = 1

for i in range(1000):
    start = start.dot(probs)

print(start)

result = [(small_to_big[i], start[i]) for i in range(n)]
result = sorted(result, key=itemgetter(1), reverse=True)

with open("page_ranks.csv", 'w') as f:
    for i, res in result:
        print(i, res, file=f)

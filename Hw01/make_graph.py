import glob
import os
import base64
from urllib.parse import urljoin

def clean_big_url(url):
    pos = url.find("://")
    if pos != -1:
        url = url[pos + 3:]
    url = "http://" + url
    if len(url) > 7 and url[-1] == "/":
        url = url[:-1]
    return url

url_to_id = {}
id_to_url = {}

with open("all_url.scv", 'r') as f:
    lines = f.readlines()
    for line in lines:
        id, url = line.split()
        id = int(id)
        try:
            url = base64.decodestring(url.encode()).decode("cp1251")
        except:
            print(url)
            continue
        url = clean_big_url(url)
        url_to_id[url] = id
        id_to_url[id] = url

graph = {}

for filename in glob.glob("url/*.txt"):
    doc_id = int(''.join(list(filter(str.isdigit, filename))))
    if doc_id not in graph:
        graph[doc_id] = []
    if doc_id not in id_to_url:
        print("AAAA")
    cururl = id_to_url[doc_id]
    with open(filename, 'r') as f:
        lines = f.readlines()
        if len(lines) == 0:
            print(f"EMPTY {filename}")
            continue
        for line in lines:
            try:
                line = line.encode().decode("cp1251")
                if line.find("://") == -1:
                    line = urljoin(cururl, line)
            except:
                pass
            line = clean_big_url(line)
            try:
                graph[doc_id].append(url_to_id[line])
            except:
                continue
                # print(f"Did not manage {line}")

with open("result_graph.csv", 'w') as f:
    for id, neighs in graph.items():
        if len(neighs) > 1:
            print(len(neighs))
        print(id, *neighs, file=f)


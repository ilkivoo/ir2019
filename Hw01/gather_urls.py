import glob
import os

url_to_id = {}
id_to_url = {}

for filename in glob.glob("pages/url*.txt"):
    doc_id = int(''.join(list(filter(str.isdigit, filename))))
    with open(filename, 'r') as f:
        url = f.readline().strip()
        url_to_id[url] = doc_id
        id_to_url[doc_id] = url

with open("all_url.scv", 'w') as f:
    for id, url in id_to_url.items():
        print(id, url, file=f)

from bs4 import BeautifulSoup
import base64

files = [f"byweb_for_course/byweb.{i}.xml" for i in range(10)]
print(files)

counter = 1

for fname in files:
    f = open(fname, "r")
    contents = f.read()
    soup = BeautifulSoup(contents, 'xml')

    for doc in soup.find_all('document'):
        if doc.docID is not None:
            file = open(f"pages/document{doc.docID.string}.txt", "bw+")
        else:
            file = open("pages/document{str(counter)}.txt", "bw+")
        counter += 1
        if doc.docID is not None:
            fileURL = open("pages/url{doc.docID.string}.txt", "w+")
            fileURL.write(doc.docURL.string)
            fileURL.close()
        if doc.content is not None:
            file.write(base64.b64decode(doc.content.text))
        file.close()
    f.close()


from bs4 import BeautifulSoup
import base64
import glob
import os

for filename in glob.glob("pages/document*.txt"):
	f = open(filename, 'rb')
	fileText = open("text1/" + os.path.basename(f.name), "w+")
	fileURL = open("url1/" + os.path.basename(f.name), "w+")
	contents = f.read()
	soup = BeautifulSoup(contents, 'lxml')
	for script in soup(["script", "style", "meta", "noscript", "head", "[document]", "title","tag"]):
	        script.extract()
	fileText.write(soup.get_text(" ").replace("\n", " ").strip())
	fileURL.write("\n".join([a['href'] for a in soup.find_all('a', href=True)]))
	fileURL.close()
	fileText.close()
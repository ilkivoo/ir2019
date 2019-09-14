import math
import os
import re
import matplotlib.pyplot as plt
from pymystem3 import Mystem
from collections import defaultdict


def isEng(word):
    flag = True
    for char in word:
        if ord(char) >= 128:
            return False
    return True


if __name__ == "__main__":
    inDirName = "/Users/alyokhina-o/Инфопоиск/Hw01.02/text1/"
    stop_words_dirname = "/Users/alyokhina-o/Инфопоиск/stopwords/"

    m = Mystem()
    filenames = []

    for (_, _, x) in os.walk(inDirName):
        filenames = x

    stop_words_filenames = []
    for (_, _, x) in os.walk(stop_words_dirname):
        stop_words_filenames = x

    stop_words = []
    for stop_words_filename in stop_words_filenames:
        fin = open(stop_words_dirname + stop_words_filename, 'r')
        text = fin.read()
        for x in text.split():
            stop_words.append(x)
    word_count = 0
    stop_word_count = 0
    dictionary = defaultdict(int)
    average_len_in_coll = 0
    eng_word_count = 0
    idf = defaultdict(set)
    i = 0
    for filename in filenames:
        fin = open(inDirName + filename, 'r')
        text = fin.read()
        lemmas = m.lemmatize(text)
        for word in lemmas:
            match = re.search("[\s\t\n;|(){},.?!':><123456789/=+*~\[\]\"-_»“…«№`‹”‚©-]+", word)
            if not match:
                if word in stop_words:
                    stop_word_count += 1
                else:
                    word_count += 1
                    average_len_in_coll += len(word)
                    dictionary[word] += 1
                    idf[word].add(filename)
                    if isEng(word):
                        eng_word_count += 1

        i += 1
    average_len_in_dict = 0
    for key in dictionary:
        average_len_in_dict += len(key)

    print("proportion of stop words: " + str(stop_word_count / word_count))
    print("average length of words in a collection: " + str(average_len_in_coll / word_count))
    print("average length of words in a dictionary: " + str(average_len_in_dict / len(dictionary)))
    print("proportion of words in Latin letters: " + str(eng_word_count / word_count))

    print("\n\n")
    sorted_dict = sorted(dictionary.items(), key=lambda t: (t[1], t[0]), reverse=True)
    for i in range(10):
        print(sorted_dict[i])

    print("\n\n")
    sorted_idf = sorted(idf.items(), key=lambda t: (len(t[1]), t[0]), reverse=True)
    for i in range(10):
        print(str(sorted_idf[i][0]) + " " + str(math.log2(len(filenames) / len(sorted_idf[i][1]))))

    x = []
    y = []
    i = 0
    for (key, value) in sorted_dict:
        i += 1
        x.append(math.log2(i))
        y.append(math.log2(value))
    plt.plot(x, y)
    plt.show()

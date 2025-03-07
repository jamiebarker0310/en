# some accessing of the semantic concordance data for wordnet 1.6
# by Des Berry, berry@ais.it

import string
import os
from wordnet import binarySearchFile

# Sample entries in the 'taglist' file
#   ordinary%1:18:01:: 1 br-a01:78,1;86,1;88,4
#   ordered%5:00:00:organized:01 2 br-j23:6,14;13,32;66,12
# where the general form is:
#   lemma%ss_type:lex_filenum:lex_id:head_word:head_id sense_number
[location_list]
#   location_list: filename:sent_num,word_num[;sent_num,word_num...]

ss_type = ("NOUN", "VERB", "ADJECTIVE", "ADVERB", "ADJECTIVE SATELLITE")

# given a sentence number (and the contents of a semantic concordance file)
# return a string of words as the sentence


def find_sentence(snum, msg):
    str = "<s snum=%s>" % snum
    s = string.find(msg, str)
    if s < 0:
        return "<Unknown>"
    s = s + len(str)
    sentence = ""
    tag = ""
    while True:
        if msg[s] == "\n":
            s = s + 1
        n = string.find(msg, "<", s)
        if n < 0:
            break
        if n - s != 0:
            if tag == "w" and msg[s] != "'" and len(sentence) > 0:  # word form
                sentence = sentence + " "
            sentence = sentence + msg[s:n]
        e = string.find(msg, ">", n)
        if e < 0:
            break
        tag = msg[n + 1]
        if tag == "/":  # check for ending sentence
            if msg[n + 2] == "s":
                # end of sentence
                break
        s = e + 1
    return sentence


# given a taglist sense (one line of the tagfile) and where to find the tagfile (root)
# return a tuple of
#  symset type ('1' .. '5')
#  sense (numeric character string)
#  list of sentences (constructed from the taglist)


def tagsentence(tag, root):
    s = string.find(tag, "%")
    sentence = []
    type = tag[s + 1]
    c = s
    for i in range(0, 4):
        c = string.find(tag, ":", c + 1)
    c = string.find(tag, " ", c + 1)
    sense = tag[c + 1]
    c = c + 3
    while True:
        d = string.find(tag, " ", c)  # file separator
        if d < 0:
            loclist = tag[c:]
        else:
            loclist = tag[c:d]
            c = d + 1

        e = string.find(loclist, ":")
        filename = loclist[:e]
        fh = open(root + filename, "rb")
        msg = fh.read()
        fh.close()

        while True:
            e = e + 1
            f = string.find(loclist, ";", e)
            if f < 0:
                sent_word = loclist[e:]
            else:
                sent_word = loclist[e:f]
                e = f

            g = string.find(sent_word, ",")
            sent = sent_word[:g]

            sentence.append(find_sentence(sent, msg))

            if f < 0:
                break

        if d < 0:
            break
    return (type, sense, sentence)


# given a word to search for and where to find the files (root)
# displays the information
# This could be changed to display in different ways!


def sentences(word, root):
    cache = {}
    file = open(root + "taglist", "rb")
    key = word + "%"
    keylen = len(key)
    binarySearchFile(file, key + " ", cache, 10)
    print("Word '%s'" % word)
    while True:
        line = file.readline()
        if line[:keylen] != key:
            break
        type, sense, sentence = tagsentence(line, root + "tagfiles/")
        print(ss_type[string.atoi(type) - 1], sense)
        for sent in sentence:
            print(sent)


def _test(word, corpus, base):
    print(corpus)
    sentences("ordinary", base + corpus + "/")


if __name__ == "__main__":
    base = "C:/win16/dict/semcor/"
    word = "ordinary"
    _test(word, "brown1", base)
    _test(word, "brown2", base)
    _test(word, "brownv", base)

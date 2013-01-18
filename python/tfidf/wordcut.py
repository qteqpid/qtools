import jieba

while True:
    words = jieba.cut(raw_input("> "),cut_all=False)
    print "Result:", "/ ".join(words)

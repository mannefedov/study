from collections import Counter
import os, codecs, string


def main():
    os.system('python WikiExtractor.py -o wiki .\zuwiki\zuwiki.xml')
    text = codecs.open('.\\wiki\\AA\\wiki_00').read()
    c = Counter()
    
    for word in text.split():
        word = ''.join([x.lower() for x in word if x not in string.punctuation and '<' not in word and x is not ''])
        if word.isalpha():
            c.update([str(word)])
    with codecs.open('word_counts.txt', 'w') as counts:
        counts.writelines([x[0] + ': ' + str(x[1]) + '\n' for x in c.most_common()])

if __name__ == '__main__':
    main()

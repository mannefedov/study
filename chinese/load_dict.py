#coding='utf-8'
import re
from lxml import etree


def load_dict():
    regex = re.compile(r'\n.*? (.*?) \[(.*?)\] /(.*)/')
    dictionary = open('cedict_ts.u8', encoding='utf-8').read()
    d = {}
    for x in re.findall(regex, dictionary):
        if d.get(x[0]) is not None:
            d[x[0]].append((x[1], x[2]))
        else:
            d[x[0]] = [(x[1],x[2])]
    return d


def translate(d, sent):
    line = ''
    s = ''
    for i in range(len(sent)):
        if sent[i] in "“ 。”，！‘…：？-、ａ； ":
                line += sent[i]
                if s:
                    line += '<w>'
                    for defin in d[s]:
                        sem = defin[1].replace('"','').replace('&','').replace('/', ',')
                        line += '<ana lex="{}" transcr="{}" sem="{}"/>{}'.format(s, defin[0], sem, s)
                    
                    line += '</w>'
                    s = ''
        else:
            s += sent[i]
            if d.get(s) is not None:
                continue
            else:
                s = s[:-1]
                line += '<w>'
                for defin in d[s]:
                    sem = defin[1].replace('"','').replace('&','').replace('/', ',')
                    line += '<ana lex="{}" transcr="{}" sem="{}"/>{}'.format(s, defin[0], sem, s)
                
                line += '</w>'
                s = ''
    return '<se>' + line + '</se>'

def main():
    d = load_dict()
    text = open('stal.xml', encoding='utf-8').read()
    text = etree.fromstring(text)
    sents = text.xpath('//se[not (@lang="ru")]')
    for sent in sents:
        sub = etree.fromstring(translate(d, sent.text))
        sent = sent.getparent().replace(sent, sub)
    etree.ElementTree(text).write('parsed.txt', encoding='utf-8', pretty_print=True)

if __name__ == '__main__':
    main()

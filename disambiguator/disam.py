import re
from collections import Counter

class Prep:
    def __init__(self, name):
        self.name = name
        self.count = 0
        self.cases = Counter()


    def __eq__(self, other):
        return self.name == other.__str__()

    def add_case(self, case):
        self.cases.update([case])
        self.count += 1

    def disambiguate(self):
        m = 0
        case = None
        for i in self.cases:
            p = self.cases[i]/self.count
            if p > m:
                m = p
                case = i
        return case

def learn_dist(corpus):
    corpus = open(corpus, 'r', encoding='utf-8')
    preps = []
    for line in corpus:
        line = line.split(' ')
        for i in range(len(line)):
            p = re.search(r'([а-яё]*)=PR=', line[i])
            if p is not None and line[i+1:] != []:
                p = p.group(1)
                if re.search(r'=S,', line[i+1]) is not None:
                    case = re.findall(r'[од|неод]=([а-яё]{1,4})', line[i+1])
                    
                    if p in preps:
                        for c in case:
                            if c:
                                preps[preps.index(p)].add_case(c)
                    else:
                        p = Prep(p)
                        for c in case:
                            if c:
                                 p.add_case(c)
                        preps.append(p)
                elif line[i+2:] != []  and re.search(r'=S,', line[i+2]) is not None:
                    case = re.findall(r'[од|неод]=([а-яё]{1,4})', line[i+2])
                    if p in preps:
                        for c in case:
                            if c:
                                 preps[preps.index(p)].add_case(c)
                    else:
                        p = Prep(p)
                        for c in case:
                            if c:
                                p.add_case(c)
                        preps.append(p)
    return preps

def disam(corpus, dist):
    new = open('new_' + corpus, 'w', encoding='utf-8')
    corpus = open(corpus, 'r', encoding='utf-8')
    trig = False
    c = 0
    prep = None
    for line in corpus:
        lines = line.split(' ')
        for line in lines:
            if c > 2:
                trig = False
                c = 0
            if trig:
                if re.search(r'=S,', line) is not None:
                    w, defin = line[:line.find('{')], line[line.find('{'):line.find('}')]
                    defin = defin.split('|')[0]
                    defin = re.sub(r'од=[а-яё]{1,4}', 'од=' + dist[dist.index(prep)].disambiguate(), defin)
                    new.write(w + defin + '}' + '\n' )

                    trig = False
                    c = 0
                elif re.search(r'=PR=', defin) is not None:
                    w, defin = line[:line.find('{')], line[line.find('{'):line.find('}')]
                    p = re.search(r'=PR=', defin)
                    if p is not None and w in dist:
                        trig = True
                        prep = w
                        new.write(line + '\n')
                else:
                    new.write(line + '\n')
                    c += 1

            else:
                w, defin = line[:line.find('{')], line[line.find('{'):]
                p = re.search(r'=PR=', defin)
                if p is not None and w in dist:
                    trig = True
                    prep = w
                new.write(line + '\n')
    corpus.close()
    new.close()

            
def main():
    pr = learn_dist('corp.txt')
    disam('corp.txt', pr)

if __name__ == '__main__':
    main()
import os
from crawler import *
import urllib.request
import subprocess
import csv


def main():
    report = {
          "path": '',  # -- это путь к файлу со статьёй,
          "author": '',  # -- имя автора, если его можно достать со страницы (и вообще если оно есть),
          "sex": '',   # -- поле оставить пустым,
          "birthday": '',   # -- оставить пустым
          "header": '',   # -- название статьи
          "created": '',   # -- дата в формате 07.01.2012 (день.месяц.год)
          "sphere": "публицистика",  #
          "genre_fi": '',   # -- оставить пустым
          "type": '',   # -- оставить пустым
          "topic": '',   # -- категория, если мы её можем найти на странице со статьёй
          "chronotop": '',   # - - оставить пустым
          "style": "нейтральный",
          "audience_age": "н-возраст",
          "audience_level": "н-уровень",
          "audience_size": "городская",
          "source": '',  # -- URL, откуда статья была скачана
          "publication": "Пензенская правда",  # -- название газеты
          "publisher": '',  # -- оставить пустой
          "publ_year": '',  # -- год публикации
          "medium": "газета",
          "country": "Россия",
          "region": 'Пензенская область',
          "language": "ru"
    }
    repotr_csv = open('corpus_meta.csv', 'w', encoding='utf-8')
    w = csv.DictWriter(repotr_csv, report.keys())
    w.writeheader()
    count = 0
    months = {'января': "01",
              'февраля': "02",
              'марта': "03",
              'апреля': "04",
              'мая': "05",
              'июня': "06",
              'июля': "07",
              'августа': "08",
              'сентября': "09",
              'октября': "10",
              'ноября': "11",
              'декабря': "12"
              }

    all_links = [x.strip('\n') for x in open('spisok.txt', encoding='utf-8')]
    for link in all_links:
        try:
            urllib.request.urlopen(link)
        except Exception:
            continue
        header = get_header(link)
        author = get_author(link)
        if author == '' or author == []:
            author = ['Nonename']
        time = get_time(link)[0].split(',')[0].split(' ')

        time[1] = months[time[1]]
        text = get_text(link)
        topic = get_topic(link)
        path = 'corpus\\' + time[2] + '\\' + time[1] + '\\plain_text\\'

        if not os.path.exists(path):
            os.makedirs(path)

        file_name = link.split('/')[:2:-1][1] + '_' + link.split('/')[:2:-1][0].replace('html', 'txt')

        with open(path + file_name, 'w', encoding='utf-8') as corpus:
            corpus.write('@au {a}\n'.format(a=author[0]))
            corpus.write('@ti {n}\n'.format(n=''.join(header)))
            corpus.write('@da {d}.{m}.{y}\n'.format(d=time[0], m=time[1], y=time[2]))
            corpus.write('@topic {t}\n'.format(t=','.join(topic)))
            corpus.write('@url {l}\n'.format(l=link))
            corpus.write(''.join([x.rstrip(' ') for x in text]))

        path_xml = 'corpus\\' + time[2] + '\\' + time[1] + '\\xml_mystem\\'
        if not os.path.exists(path_xml):
            os.makedirs(path_xml)
        path_mystem = 'corpus\\' + time[2] + '\\' + time[1] + '\\mystem\\'
        if not os.path.exists(path_mystem):
            os.makedirs(path_mystem)

        with open(path_xml + file_name, 'w', encoding='utf-8') as temp:
            temp.write(''.join([x.rstrip(' ') for x in text]))
        subprocess.call(['mystem', '-e UTF-8 ', '-icd', '--format', 'xml'], stdin=open(path_xml + file_name, encoding='utf-8'), stdout=open(path_xml + file_name.replace('.txt', '_m.xml'), 'w', encoding='utf-8'))
        subprocess.call(['mystem', '-e UTF-8 ', '-icd'], stdin=open(path_xml + file_name, encoding='utf-8'), stdout=open(path_mystem + file_name.replace('.txt', '_m.txt'), 'w', encoding='utf-8'))

        os.remove(path_xml + file_name)
        report['path'] = path + file_name
        report["author"] = author[0]
        report["created"] = '{d}.{m}.{y}'.format(d=time[0], m=time[1], y=time[2])
        report["topic"] = '{t}'.format(t=','.join(topic))
        report["source"] = link
        report["publ_year"] = time[2]
        w.writerow(report)

        count += 1
        print(count)
    repotr_csv.close()
if __name__ == '__main__':
    main()


import requests
import re
import os
import time

def request_ogrn(ogrn, r):
    x = r.get('http://огрн.онлайн/интеграция/компании/?огрн={}'.format(ogrn))
    if x.status_code == 200:
        x = x.json()
        if x and x[0] is not None:
            return x[0]['id']


def request_id(company_id, r):
    x = r.get('http://огрн.онлайн/интеграция/компании/{}/'.format(company_id))
    if x.status_code == 200:
        x = x.json()
        if x is not None:
            return x


def parse_text(text_file):
    text = open(text_file, encoding='utf-8').read()
    ogrn = re.findall(r'огрн *?([0-9]{13})', text)
    if ogrn is not None:
        return ogrn


def find_ogrns(start, offset=10):
    os.chdir('stemmed_texts')
    files = os.listdir()
    table = []
    n_of_ogrns = 0
    for f in files[start:start + offset]:
        ogrns = parse_text(f)
        if not ogrns:
            continue
        table += [(f.strip('.txt'), ogrn) for ogrn in ogrns]
        n_of_ogrns += 1
    os.chdir('..')
    return table, n_of_ogrns

def ogrn_to_id(table, start, offset=50):
    result = {}
    st = time.time()
    r = requests.Session()
    for x in table[start:offset+start]:
        t = time.time() - st
        if t < 0.45:
            time.sleep(0.45 - t)
        try:
            y = request_ogrn(x[1], r)
            if y is not None:
                result[x[1]] = y
                st = time.time()
        except Exception:
            print(x)
            print('ogrn - {}; file - {}'.format(x[1], x[0]))
            raise
    return result


def get_info(table):
    r = requests.Session()
    result_table = []
    start = time.time()
    broken_id = []
    for ogrn in table:
        if len(broken_id) ==  10:
            print('Warning: 10 ids are broken already, sleep for 50 secs')
            time.sleep(50)
            r = requests.Session()
        elif len(broken_id) > 20:
            print('Warning: 20 ids are broken already, sleep for 100 secs')
            time.sleep(100)
            r = requests.Session()
        t = time.time() - start
        if t < 0.45:
            time.sleep(0.45 - t)
        try:
            info = request_id(table[ogrn], r)
            start = time.time()
            if info is None:
                broken_id.append(table[ogrn])
                print('Bad response on id {}; sleeping for 10 seconds...'.format(table[ogrn]))
                time.sleep(10)
                continue
            okopf = info['okopf']['code'] if info.get('okopf') is not None else None
            okved1 = info['mainOkved1']['code'] if info.get('mainOkved1') is not None else None
            okved2 = info['mainOkved2']['code'] if info.get('mainOkved2') is not None else None
            result_table.append((str(table[ogrn]), str(okopf), str(okved1), str(okved2)))
        except Exception as e:
            print("{} - ogrn; {} - id".format(ogrn, table[ogrn]))
            raise(e)
    return result_table, broken_id

if __name__ == '__main__':
    table = []
    f = open('file_ogrn.tsv', encoding='utf-8')
    for line in f:
        line = line.strip('\n')
        x, y = line.split('\t')
        table.append((x, y))
    try:
        params = open('params_on_error.tsv', encoding='utf-8').read()
        params = params.strip('\n').split('\t')
        # all_files = int(params[0])
        # files_with_ogrn = int(params[1])
        # ogrns = int(params[2])
        ogrn_with_id = int(params[0])
        id_with_info = int(params[1])
        p = int(params[2])
    except Exception:   
        ogrn_with_id = 0
        id_with_info = 0
        p = 0
    all_files = 102153
    files_with_ogrn = 59814
    ogrns = len(table)
    broken_ids = []
    for i in range(p, len(table), 50):
        st = time.time()
        # file_ogrn_table, n = find_ogrns(start=i)
        # stats 1
        # all_files += i
        # files_with_ogrn += n

        # with open('file_ogrn.tsv', 'a', encoding='utf-8') as f:
        #     for file_ogrn_pair in file_ogrn_table:
        #         f.write('\t'.join(file_ogrn_pair) + '\n')
        try:
            ogrn_id_table = ogrn_to_id(table, i)
        # stat 2
            ogrn_with_id += len(ogrn_id_table)
            with open('ogrn_id.tsv', 'a', encoding='utf-8') as f:
                for ogrn in ogrn_id_table:
                    f.write('\t'.join((str(ogrn), str(ogrn_id_table[ogrn]))) + '\n')

            info, broken_id = get_info(ogrn_id_table)
            broken_ids += broken_id
            n = [1 for i in range(len(info)) if any([info[i][1], info[i][2], info[i][3]])]
            id_with_info += len(n)
            with open('info_table.tsv', 'a', encoding='utf-8') as result_table:
                for inf in info:
                    result_table.write('\t'.join((str(x) for x in inf)) + '\n')
            ogrn_to_file_stat = (files_with_ogrn / all_files) * 100
            ogrn_to_id_stat = (ogrn_with_id / ogrns) * 100
            id_to_info_stat = (id_with_info / ogrn_with_id) * 100
            print('----------------------------------')
            print('Percentage of ogrn in texts - {:.2f} %'.format(ogrn_to_file_stat))
            print('Percentage of ogrn with id - {:.2f} %'.format(ogrn_to_id_stat))
            print('Percentage of id with any info - {:.2f} %'.format(id_to_info_stat))
            print('Time taken {}'.format(time.time() - st))
            print('Processed {} texts...'.format(i + 50))
        except Exception as e:
            with open('params_on_error.tsv', 'w', encoding='utf-8') as log_er:
                log_er.write('\t'.join([ogrn_with_id, id_with_info, i]))
            with open('brokens.txt', 'a', encoding='utf-8') as broken:
                broken.write('\n'.join(broken_ids))
    with open('broken.txt', 'a', encoding='utf-8') as broken:
        broken.write('\n'.join(broken_ids))

    
            


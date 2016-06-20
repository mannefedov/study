
def main():
    table = open('table.csv', encoding='utf-8')
    text = open('текст.txt', encoding='utf-8')
    result = open('amhar_transl.txt', 'a', encoding='utf-8')

    lookupdict = {}
    new_table = []

    # создаем промежуточную таблицу 
    for line in table:
        line = line.strip('\n').split('\t')
        new_table.append(line)
    # создаем на основе промежуточной таблицы словарь сотвествтий
    for i in range(len(new_table)):
        for j in range(len(new_table[i])):
            if i != 0 and j != 0:
                lookupdict[new_table[i][j]] = new_table[i][0] + new_table[0][j]
    # сопоставляем тексту транскрипции и записываем в файл
    for line in text:
        for i in line:
            if i in lookupdict:
                result.write(lookupdict[i])
            else:
                result.write(i)
    text.close()
    table.close()
    result.close()

if __name__ == '__main__':
    main()

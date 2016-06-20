import csv

table = open('lettertable.csv', newline='', encoding='utf-8')
fil = open('gimnofgeorgia.txt', 'r', encoding='utf-8')
text = open('a.txt', 'w', encoding='utf-8')

letters = csv.reader(table, delimiter='\t',)
lookUpdict = {}

for line in letters:
    lookUpdict[line[0]] = line[2]
# заполняет словарь. ключ словаря - буква, значение - транскрипция этой буквы


for i in fil.read():
    if i in lookUpdict:
        text.write(lookUpdict[i])
    else:
        text.write(i)
# читает каждый символ в тексте. если символ есть в словаре, записывает его транскрипцию в отдельный файл
# если символа нет в словаре, записывает сам символ.

table.close()
text.close()
fil.close()


import re, urllib.request
import lxml.html, os


def get_links(link):
    
    # link = urllib.request.urlopen(link).read()
    page = lxml.html.parse(link).getroot()
    data = page.xpath('.//a/@href')
    articles = [x for x in data if '.ru/topic/' in x or '/oldnews/' in x]
    articles = [x for x in articles if '#' not in x and x.endswith('html')]
    links_list = list(set([x for x in data if 'pravda-news.ru/' in x]))
    return links_list, set(articles)


def web_crawler(base_link, number=2500):
    arts = set()
    active_links = [base_link]
    visited_links = []
    for link in active_links:
        links_list, articles = get_links(link)
        arts.update(articles)
        visited_links.append(link)
        active_links.remove(link)

        for link in links_list:
            if link not in visited_links and link not in active_links:
                active_links.append(link)
        if len(arts) > number:
            break
        print(str(len(arts)))
    return arts

def get_author(link):
    page = lxml.html.parse(link).getroot()
    data = page.xpath('.//div[@class="author"]/span/a/text()')
    return data


def get_time(link):
    page = lxml.html.parse(link).getroot()
    data = page.xpath('.//div[@class="wrapper_time"]/time/text()')
    if data == []:
        data = page.xpath('.//article[@class="topic"]/time/text()')
    return data

def get_header(link):
    page = lxml.html.parse(link).getroot()
    data = page.xpath('.//article[@class="topic"]/h1/text()')
    return data

def get_text(link):
    page = lxml.html.parse(link).getroot()
    data = page.xpath('.//div[@class="content"]/sape_index/p/text()')
    return data


def get_topic(link):
    page = lxml.html.parse(link).getroot()
    data = page.xpath('.//div[@class="block border-bottom"]/div[@class="terms"]/a/text()')
    return data


if __name__ == "__main__":
    base_link = 'http://www.pravda-news.ru/'
    urls = web_crawler(base_link)
    with open('spisok.txt', 'w', encoding='utf-8') as spisok:
        for x in urls:
            spisok.write(x + '\n')


# Чтобы достать автора нужно: 
 # на выходе список [Мария ЕНГАЛЫЧЕВА]

# Чтобы доставть время нужно:
# 

# Для заголовка:
# 

# Для текста статьи
# 

# Для ссылок:
# data = page.xpath('.//a/@href')
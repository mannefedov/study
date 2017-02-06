# основные функции
# у всех на вход подается две строки с нормализованными предложениями
# где у каждого слова через подчеркивание добавлена часть речи

from scipy.spatial.distance import cosine
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.stats import binned_statistic
from gensim.models import Word2Vec as w2v

# word2vec модель
model = w2v.load_word2vec_format('news_10.bin', binary=True)
model.similarity('полиция_S', 'милиция_S')

# собираем idf по корпусу
v = TfidfVectorizer()
v.fit(corpus) 
idf = v.idf_
weights = dict(zip(v.get_feature_names(), idf))

# cредняя длинна всех предложений для функции "weighted_sum"
avg_d = sum([len(x.split()) for x in corpus])/len(corpus)

# бины (bins) или группы в функциях я взял из статьи, их можно заменить на сумму всех значений или среднее

def vec_sim(x, y):
    """близость через ворд2век"""
    x = x.split()
    y = y.split()
    if not x or not y:
        return 0
    return model.n_similarity(x, y)

def vec_sim_mean(x, y):
    """Близость через косинус, по сумме векторов слов, взвешенная по idf
       Значение по умолчанию я не знал, как выбрать и поставил просто 1
       Можно поменять сумму на среднее, результат одинаковый"""
    if not x or not y:
        return 0
    x = x.split()
    y = y.split()
    
    x = np.array([model[x_i]*weights.get(x_i.lower(), 1) for x_i in x]).sum(axis=0)
    y = np.array([model[y_i]*weights.get(y_i.lower(), 1) for y_i in y]).sum(axis=0)

    return 1.0 - cosine(x, y)

def mean_bins(x, y):
    """ Считает взвешенное среднее по векторам слов в предложении
        Потом считает длину (magn) 
        Cчитает произведение векторов
        Затем каждый элемент в произведении делится на длину
        Получается почти косинусное расстояние, но вместо суммы этих значений
        они раскладываются на 4 группы по возрастанию
        Значения я подбирал наугад и наверное можно лучше
        Я старался сделать так, чтобы в 1 группе были наиболее непохожие компоненты,
        а в последней наиболее похожие
        Количество значений в каждой группе делится на общее количество, чтобы получилось процентное соотношение
        
        """
    if not x or not y:
        return [1.0, 0,0,0]
    x = x.split()
    y = y.split()
    c_x = Counter(x)
    c_y = Counter(y)

    x = np.array([model[x_i]*weights.get(x_i.lower(), 1) for x_i in x]).mean(axis=0)
    y = np.array([model[y_i]*weights.get(y_i.lower(), 1) for y_i in y]).mean(axis=0)
    magn = np.sqrt(x.dot(x)) * np.sqrt(y.dot(y))
    v = [x/magn for x in x*y]
    bins = binned_statistic(v,v,statistic='count',bins=[-1,0.0001,0.001,1])[0]
    return [x/len(v) for x in bins]

def max_sim(word, sent):
    """Вспомогательная функция
       Считает максимальную близость слова по отношению ко всем слов в предложении"""
    return max([model.similarity(word, x) for x in sent.split()])

def weighted_sum(x, y):
    """Измененная BM25
       Предложения сортируются по длине, чтобы всегда сравнивать относительно короткого;
       Считается tf, хотя она впринципе не нужна и можно только idf оставить;
       Числа в формуле (k, b параметры, сейчас они 2 и 0.7) - для регуляризации и можно их крутить, они не сильно меняют дело
       В цикле для каждого слова в длинном предложении считается макс. близость
       относительно короткого предложения (два раза), 
       В числитель идет макс.близость умноженая на (1+k),
       В заменатель идет макс. близость + k*(1 - b + b*(len(короткое_предложение)/средняя_длинна_предл_в_корпусе);
       считается отношение между ними и умножается на tfidf для текущего слова
       
       Значения можно проссумировать или нормировать как-то, 
       или поделить на группы по возрастанию значения, но значения получаются не от 0 до 1 и не понятно
       где границы проводить
    
       
       """
    if not x or not y:
        return [1.0, 0, 0, 0]
    
    long, short = sorted([x,y], key=lambda x: len(x.split()))
    summands = []
    c = Counter(long.split())

    for word in long.split():
        s = (c[word]/len(long.split()))*weights.get(word.lower(), 1)*((max_sim(word, short)*(1+2))/(max_sim(word, short) 
                                                                        + 2*(1 - 0.7 + 0.7*(len(short)/avg_d))))
        summands.append(s)
    
    bins = binned_statistic(summands, summands, statistic='count', bins=[0, 0.25, 0.5, 0.8, float('Inf')])[0]
    return bins

def cum_sim(x, y):
    """Считает близость между всеми словами в предложениях
       Значения разбиваются по группа, группы нормализуются по общему количеству значений, 
       результат был от 0 до 1"""

    if not x or not y:
        return [1.0,0,0,0]
    x = x.split()
    y = y.split()
    
    matrix = []
    for i in x:
        for j in y:
            matrix.append(model.similarity(i, j))
    bins = binned_statistic(matrix, matrix, statistic='count', bins=(0,0.1,0.3,0.5,1), range=(0, 1))[0]
    return [x/len(matrix) for x in bins]

def max_bins(x, y):
    """Считает только максимальные близости для каждого слова в длинном предложении,
       относительно всех слов в коротком
       Делит их на группы как и предыдущих"""
    if not x or not y:
        return [1.0, 0,0]
    
    long, short = sorted([x,y], key=lambda x: len(x.split()))
    
    sim = [max_sim(x_i, short) for x_i in long.split()]
    bins = binned_statistic(sim, sim, statistic='count', bins=3, range=(0,1))[0]
    return [x/len(sim) for x in bins]
    

import pandas as pd
import numpy as np
import math
import random
import time
from sklearn import preprocessing
from sklearn.decomposition import TruncatedSVD

NUM_POPULATION = 20
NUM_SURVIVED = 0.65  # should be in range [0;1]
NUM_CHILD = 10
RATE_MUTATION = 0.05
BEST = 10

DATA = pd.DataFrame()
DIST = []
N = 0


# normalize the entire dataset using min-max scaler
def normalize(dataset):
    min_max_scaler = preprocessing.MinMaxScaler()
    # min_max_scaler = preprocessing.StandardScaler()
    x_scaled = min_max_scaler.fit_transform(dataset)
    return x_scaled


def euclidean_dist(a, b):
    d = 0
    for i in range(0, len(a)):
        if math.isnan(a[i]) or math.isnan(b[i]):
            continue
        d += (a[i] - b[i]) ** 2
    return math.sqrt(d)


def get_dist_matrix(df):
    n = df.shape[0]
    dist = [[] for i in range(n)]
    for i in range(n):
        dist[i] = [0 for i in range(n)]

    for i in range(n):
        for j in range(i + 1, n):
            dist[i][j] = euclidean_dist(df[i], df[j])
            dist[j][i] = dist[i][j]
    return dist


def fit_function(d_star, d):
    s = 0
    s_d_star = 0
    for i in range(len(d)):
        for j in range(i + 1, len(d)):
            if d_star[i][j] == 0:
                continue
            s += (d_star[i][j] - d[i][j]) ** 2 / (d_star[i][j])
            s_d_star += d_star[i][j]
    e = s / s_d_star
    return e


def selection(p):
    # p.sort(key=lambda x: x.fit_score, reverse=True)
    p.sort(key=lambda x: x.fit_score)
    return p


def get_names(df, index):
    return df.columns[[index]]


def get_table(data, index):
    return data.iloc[:, index]


def gen_chr():
    chromosomes = [random.random() for _ in range(N)]
    return chromosomes


def get_indexes(chromosomes):
    global N
    indexes = []
    for i in range(N):
        indexes.append([i, chromosomes[i]])
    indexes.sort(key=lambda x: x[1], reverse=True)
    indexes = indexes[:BEST]
    # if chromosomes[i]:
    #     indexes.append(i)
    return [indexes[i][0] for i in range(BEST)]


def calc_fit_score(indexes):
    global DATA
    table = get_table(DATA, indexes)
    dist = get_dist_matrix(table.to_numpy())
    return fit_function(dist, DIST)


class Table:
    chromosomes = []
    fit_score = 0
    indexes = []

    def __init__(self, chromosomes):
        self.chromosomes = chromosomes
        self.indexes = get_indexes(self.chromosomes)
        self.fit_score = calc_fit_score(self.indexes)

    def crossover(self, other):
        NUM_CHR = len(self.chromosomes)
        mask = [random.random() > 0.5 for _ in range(NUM_CHR)]
        child = [0.0 for _ in range(NUM_CHR)]
        for i in range(NUM_CHR):
            if mask[i]:
                child[i] = other.chromosomes[i]
            else:
                child[i] = self.chromosomes[i]
            # MUTATION
            if random.random() < RATE_MUTATION:
                child[i] = random.random()

        return child


def start(best):
    global DATA, N, DIST, BEST
    start_time = time.time()
    DATA = pd.read_csv('49.csv')
    df = normalize(DATA)
    BEST = best
    # df_ = df.to_numpy()
    N = DATA.shape[1]
    DIST = get_dist_matrix(df)

    # dist_matrix = get_dist_matrix(df.to_numpy())
    p = [Table(gen_chr()) for _ in range(NUM_POPULATION)]
    for i in range(100):
        p = selection(p)
        if i % 10 == 0:
            print(i, p[0].fit_score, len(get_names(DATA, p[0].indexes)))
            # print(i, p[0].fit_score, get_names(DATA, p[0].indexes))
            pass
        survived = p[:int(NUM_POPULATION * NUM_SURVIVED)]
        best_survived = p[:int(NUM_POPULATION * 0.3)]
        children = []

        for j in range(NUM_CHILD):
            pair = np.random.choice(best_survived, 2, replace=False)
            # father = max(pair[0].fit_score, pair[1].fit_score)
            # mother = min(pair[0].fit_score, pair[1].fit_score)
            ch = pair[0].crossover(pair[1])
            c = Table(ch)
            children.append(c)
        children = selection(children)
        children = children[
                   :NUM_POPULATION - int(NUM_POPULATION * NUM_SURVIVED)]

        p = survived + children
        p = selection(p)

    p = selection(p)
    print("Error:", p[0].fit_score)

    names = get_names(DATA, p[0].indexes)
    print("Total:", len(names), " vs ", N)
    for name in names:
        print(name)
    elapsed_time = time.time() - start_time
    print("TIME: ", elapsed_time)
    return names


if __name__ == "__main__":
    start(30)

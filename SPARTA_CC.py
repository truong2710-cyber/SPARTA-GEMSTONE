from math import dist

from CMFA import *
from IO import *
from SPARTA import SPARTA

seed(random_seed)


class Vertex(object):
    def __init__(self, T, index):
        self.T = T
        self.v = T.v
        self.neigh = []
        self.q = T.q
        self.index = index
        self.p = None


def find_set(v, parent):
    if v == parent[v]:
        return v
    p = find_set(parent[v], parent)
    parent[v] = p
    return p


def union_sets(a, b, parent):
    a = find_set(a, parent)
    b = find_set(b, parent)
    if (a != b):
        parent[b] = a


def Cluster(T, Rs):
    C = []

    n = len(T)
    parent = [i for i in range(n)]

    V = [Vertex(T[i], i) for i in range(n)]
    E = []
    for i in range(n - 1):
        for j in range(i + 1, n):
            if dist(V[i].v, V[j].v) <= 2 * Rs:
                if find_set(i, parent) == find_set(j, parent):
                    continue
                union_sets(i, j, parent)

    for i in range(n):
        V[i].p = find_set(i, parent)

    V.sort(key=lambda x: x.p)
    minp = V[0].p
    maxp = V[-1].p
    Vindex = 0
    for p in range(minp, maxp + 1):
        C.append([])

        while Vindex < n and V[Vindex].p == p:
            C[p - minp].append(V[Vindex].T)
            Vindex += 1

    temp = C.count([])
    for i in range(temp):
        C.remove([])

    return C


def SPARTA_CC(T, Rs):
    C = Cluster(T, Rs)
    S = []
    Tc = []
    for i in range(len(C)):
        Tc.append([])
        for j in range(len(C[i])):
            Tc[i].append(C[i][j])

    for i in range(len(C)):
        Sq = SPARTA(Tc[i], Rs)
        S += Sq

    return S
import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from CONSTANT import *
from random import *
import matplotlib.pyplot as plt
from math import *


class Graph():
    def __init__(self, vertices):
        self.V = vertices
        self.graph = [[0 for column in range(vertices)]
                      for row in range(vertices)]

    def get_path(self, parent):
        ans = [[parent[i], i] for i in range(1, self.V)]
        return ans

    def minKey(self, key, mstSet):

        _min = sys.maxsize

        for v in range(self.V):
            if key[v] < _min and mstSet[v] is False:
                _min = key[v]
                min_index = v

        return min_index

    def primMST(self):

        key = [sys.maxsize] * self.V
        parent = [None] * self.V
        key[0] = 0
        mstSet = [False] * self.V

        parent[0] = -1

        for _ in range(self.V):

            u = self.minKey(key, mstSet)

            mstSet[u] = True

            for v in range(self.V):

                if 0 < self.graph[u][v] < key[v] and not mstSet[v]:
                    key[v] = self.graph[u][v]
                    parent[v] = u

        return self.get_path(parent)


# GEMSTONE Constraint
def GEMSTONE(base, T, Rc):
    # base: Coordinates of base
    # GS = {GS1, GS2, ..., GSm} which GSi = set of sensor that covered Target i
    # Rc: Radius of Relay Nodes

    # arange GS
    T.sort(reverse=True, key=lambda x: len(x.Sensors))
    Qmax = T[0].q

    for i in range(1, len(T)):
        j = 0
        while j < len(T[i].Sensors):
            if T[i].Sensors[j] != 0:
                for k in range(i):
                    if T[i].Sensors[j] in T[k].Sensors:
                        l = T[k].Sensors.index(T[i].Sensors[j])
                        T[i].Sensors[j] = 0
                        if l < len(T[i].Sensors):
                            T[i].Sensors[j], T[i].Sensors[l] = T[i].Sensors[l], T[i].Sensors[j]
                            j -= 1
                        break
            j += 1

    # devide paths
    paths = []
    for q in range(T[0].q):
        paths.append([])

        for i in range(len(T)):
            if q >= len(T[i].Sensors):
                break
            if T[i].Sensors[q] != 0:
                paths[q].append(T[i].Sensors[q])

    Vs = []

    # do Prim for each path
    for q in range(T[0].q):
        temp_S = [base] + paths[q]
        temp_n = len(temp_S)
        g = Graph(temp_n)
        g.graph = [[dist(temp_S[i].v, temp_S[j].v) for j in range(temp_n)] for i in range(temp_n)]

        Vs.append([[base] + paths[q], g.primMST()])

    # compute number of relay nodes
    Rn = []
    for q in range(len(Vs)):
        P = Vs[q][0]
        E = Vs[q][1]

        for i in range(len(Vs[q][0]) - 1):
            P1 = P[E[i][0]].v
            P2 = P[E[i][1]].v
            c = dist(P1, P2)
            add = int((c - 1) // (Rc))

            for j in range(add):
                x = P1[0] + (j + 1) * (P2[0] - P1[0]) / (add + 1)
                y = P1[1] + (j + 1) * (P2[1] - P1[1]) / (add + 1)
                z = P1[2] + (j + 1) * (P2[2] - P1[2]) / (add + 1)

                sensor = (x, y, z)
                Rn.append(sensor)

    conn = []
    for V, E in Vs:
        for e in E:
            P1 = V[e[0]]
            P2 = V[e[1]]
            conn.append([P1, P2])

    return Rn, conn
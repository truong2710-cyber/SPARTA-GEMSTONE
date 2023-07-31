from SPARTA_CC import *


class Graph:
    def __init__(self, vertices):
        self.vertices = vertices
        self.graph = [[0] * vertices for _ in range(vertices)]

    def add_edge(self, u, v, capacity=1):
        self.graph[u][v] = capacity

    def bfs(self, source, sink, parent, graph):
        visited = [False] * self.vertices
        queue = [source]
        visited[source] = True

        while queue:
            u = queue.pop(0)
            for v in range(self.vertices):
                if not visited[v] and graph[u][v] > 0:
                    queue.append(v)
                    visited[v] = True
                    parent[v] = u
                    if v == sink:
                        return True

        return False

    def ford_fulkerson(self, source, sink):
        self.temp_graph = [[self.graph[i][j] for j in range(self.vertices)] for i in range(self.vertices)]

        parent = [-1] * self.vertices
        max_flow = 0

        while self.bfs(source, sink, parent, self.temp_graph):
            path_flow = float("Inf")
            s = sink

            while s != source:
                path_flow = min(path_flow, self.temp_graph[parent[s]][s])
                s = parent[s]

            max_flow += path_flow

            v = sink
            while v != source:
                u = parent[v]
                self.temp_graph[u][v] -= path_flow
                self.temp_graph[v][u] += path_flow
                v = parent[v]

        return max_flow


class Vertex:
    def __init__(self, V, index):
        """
        V: a Cluster object since each cluster is a vertex in the graph
        """
        self.V = V
        self.deg = 0
        self.index = index


class Edge:
    def __init__(self, A, B):
        """
        A, B: Two Vertex objects
        """
        self.V1 = A
        self.V2 = B
        self.dist = dist(A.V.Center.v, B.V.Center.v)


class Cluster:
    def __init__(self, Center, Targets, Qmax):
        """
        Center: a Target object which is the center of the cluster
        Targets: list[Targets]: all targets in the cluster (except the center)
        """
        self.Center = Center
        self.Targets = Targets
        self.e = -1
        if type(Center) == Base:
            self.e = Qmax
        else:
            for Ti in [Center] + self.Targets:
                if Ti.q > self.e:
                    self.e = Ti.q

    def insert_anchor_node(self, S, Rn, Rs):
        for i in range(self.e - self.Center.q):
            temp_s = Sensor(self.Center.v, Rs, [self.Center])
            self.Center.Sensors.append(temp_s)
            S.append(temp_s)
            Rn.append(self.Center.v)

    def put_relay(self, S, Rn, Rc, Rs):
        ans = []
        self.insert_anchor_node(S, Rn, Rs)

        for Ti in self.Targets:
            used = []
            for Sij in Ti.Sensors:
                for Sk in self.Center.Sensors:
                    if Sk not in used:
                        ans.append([Sij, Sk])
                        used.append(Sk)
                        break

        for Si, Sj in ans:
            c = dist(Si.v, Sj.v)
            add = int((c - 0.0001) // Rc)
            for j in range(add):
                x = Si.v[0] + (j + 1) * (Sj.v[0] - Si.v[0]) / (add + 1)
                y = Si.v[1] + (j + 1) * (Sj.v[1] - Si.v[1]) / (add + 1)
                z = Si.v[2] + (j + 1) * (Sj.v[2] - Si.v[2]) / (add + 1)

                sensor = (x, y, z)
                Rn.append(sensor)

        return ans


def clustering(T, Rcl, Qmax):
    C = []
    used = []

    while True:
        maxneigh = float("-inf")

        bestT = None
        bestNeighs = []

        for Ti in T:
            if Ti not in used:
                center = Ti
                neighbours = []
                for Tj in T:
                    if Ti != Tj and Tj not in used:
                        if dist(Ti.v, Tj.v) <= Rcl:
                            neighbours.append(Tj)

                    if len(neighbours) > maxneigh:
                        maxneigh = len(neighbours)
                        bestT = center
                        bestNeighs = neighbours

        if bestT == None:
            break

        C.append(Cluster(bestT, bestNeighs, Qmax))
        used.append(bestT)
        used += bestNeighs

    return C


def construct_edge(C, base, Qmax):
    B = Cluster(base, [], Qmax)
    V = [Vertex(B, 0)] + [Vertex(C[i], i + 1) for i in range(len(C))]
    L = []
    E = []

    for i in range(1, len(V)):
        for j in range(i):
            L.append(Edge(V[i], V[j]))

    L.sort(key=lambda x: x.dist)

    for Li in L:
        V1, V2 = Li.V1, Li.V2

        if V1.deg < V1.V.e or V2.deg < V2.V.e:
            E.append(Li)
            V1.deg += 1
            V2.deg += 1

    for r in E:
        L.remove(r)

    for i in range(1, len(V)):
        G = Graph(len(C) + 1)

        for Ei in E:
            G.add_edge(Ei.V1.index, Ei.V2.index)
            G.add_edge(Ei.V2.index, Ei.V1.index)

        source = V[i].index
        sink = V[0].index

        max_flow_value = G.ford_fulkerson(source, sink)

        if max_flow_value < V[i].V.e:
            while max_flow_value < V[i].V.e:
                E.append(L[0])
                G.add_edge(L[0].V1.index, L[0].V2.index)
                G.add_edge(L[0].V2.index, L[0].V1.index)
                max_flow_value = G.ford_fulkerson(source, sink)
                L.remove(L[0])

    return E


def put_relay_along_edges(A, B, Rn, Rc):
    P1 = A.v
    P2 = B.v
    c = dist(P1, P2)
    add = int((c - 0.0001) // Rc)
    for j in range(add):
        x = A.v[0] + (j + 1) * (B.v[0] - A.v[0]) / (add + 1)
        y = A.v[1] + (j + 1) * (B.v[1] - A.v[1]) / (add + 1)
        z = A.v[2] + (j + 1) * (B.v[2] - A.v[2]) / (add + 1)

        sensor = (x, y, z)
        Rn.append(sensor)

    return 0


def CMFA(base, T, S, Rc, Rcl, Rs, Qmax):
    C = clustering(T, Rcl, Qmax)

    Rn = []

    intra_conn = []
    for Ci in C:
        intra_conn.extend(Ci.put_relay(S, Rn, Rc, Rs))

    E = construct_edge(C, base, Qmax)

    inter_conn = []
    for Ei in E:
        put_relay_along_edges(Ei.V1.V.Center, Ei.V2.V.Center, Rn, Rc)
        inter_conn.append([Ei.V1.V.Center, Ei.V2.V.Center])

    conn = intra_conn + inter_conn

    return Rn, conn
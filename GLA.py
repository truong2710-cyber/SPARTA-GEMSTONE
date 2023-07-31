import math
from math import dist
from numpy import sqrt, dot, cross
from numpy.linalg import norm
from ortools.linear_solver import pywraplp
from IO import *

seed(CONSTANT.random_seed)


def random_point_in_sphere(center, radius):
    x0, y0, z0 = center
    # Generate random spherical coordinates (r, theta, phi)
    r = radius * random() # To ensure uniform distribution within the sphere
    theta = 2 * math.pi * random()
    phi = 2 * math.pi * random()

    # Convert spherical coordinates to Cartesian coordinates
    x = x0 + r * math.sin(phi) * math.cos(theta)
    y = y0 + r * math.sin(phi) * math.sin(theta)
    z = z0 + r * math.cos(phi)

    return [x, y, z]


def solve(n, regions, q):
    """
    n (int): number of targets
    regions (list): list of region to place sensor. Example: [[1,2,3],[3,4]]
    q (list): priority vector
    """
    solver = pywraplp.Solver.CreateSolver('SCIP')
    x = [[]] * len(regions)
    for i in range(len(regions)):
        x[i] = solver.IntVar(0, solver.infinity(), ' ')
    for j in range(n):
        solver.Add(solver.Sum([x[i] for i in range(len(regions)) if j in regions[i]]) >= q[j])
    M = solver.Sum(x)
    opjective = solver.Minimize(M)
    solver.Solve()
    return [int(x[i].solution_value()) for i in range(len(regions))]


def trilaterate(P1, P2, P3, r1, r2, r3):
    """
    @param P1: point 1
    @param P2: point 2
    @param P3: point 3
    @param r1: radius 1
    @param r2: radius 2
    @param r3: radius 3
    @return: points satisfying trilateration.
    """
    v12 = [P2[i] - P1[i] for i in range(3)]
    d = norm(v12)
    e_x = v12 / norm(v12)
    v13 = [P3[i] - P1[i] for i in range(3)]
    i = dot(e_x, v13)
    temp3 = v13 - i * e_x
    e_y = temp3 / norm(temp3)
    e_z = cross(e_x, e_y)
    j = dot(e_y, v13)
    x = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
    y = (r1 * r1 - r3 * r3 - 2 * i * x + i * i + j * j) / (2 * j)
    temp4 = r1 * r1 - x * x - y * y
    if temp4 < 0:
        return False, False
    z = sqrt(temp4)
    p_12_a = P1 + x * e_x + y * e_y + z * e_z
    p_12_b = P1 + x * e_x + y * e_y - z * e_z
    return list(p_12_a), list(p_12_b)


class IntersectionPoint(object):
    def __init__(self, v, parent, is_3D=True):
        self.v = v
        self.parent = parent
        self.cover = []
        self.is_3D = is_3D

    def is_cover(self, D):
        if D not in self.cover:
            if dist(self.v, D.v) <= D.R or D in self.parent:
                return True

        return False

    def is_remove(self, rD):
        if self.parent[0] in rD or self.parent[1] in rD or self.parent[2] in rD:
            return True

        return False

    def remove_cover(self, rD):
        for r in rD:
            if r in self.cover:
                self.cover.remove(r)


class Sphere(object):
    def __init__(self, T, R, index):
        self.T = T
        self.v = T.v
        self.q = T.q
        self.R = R
        self.index = index
        self.pair = []
        self.intersections = []
        self.best_point = []
        self.alone = False

    def find_best_point(self):
        self.intersections.sort(reverse=True, key=lambda x: len(x.cover))
        self.best_point.append(self.intersections[0])

        for i in range(1, len(self.intersections)):
            if self.intersections[i].cover == self.intersections[0].cover:
                # point B
                self.best_point.append(self.intersections[i])
                break


# Finding sensors
def GLA(T, Rs):
    n = len(T)
    D = [Sphere(T[i], Rs, i) for i in range(n)]  # set of Sphere
    D.sort(key=lambda x: x.q)
    S = []  # set of sensor

    # find triad
    for i in range(n - 2):
        for j in range(i + 1, n - 1):
            for k in range(j + 1, n):
                p1, p2 = trilaterate(D[i].v, D[j].v, D[k].v, Rs, Rs, Rs)
                if p1 and p2:
                    parent = (D[i], D[j], D[k])
                    for child in parent:
                        child.intersections.append(IntersectionPoint(p1, parent))
                        child.intersections.append(IntersectionPoint(p2, parent))

    # find pair
    for i in range(n):
        if len(D[i].intersections) == 0:
            for j in range(n):
                if i != j:
                    if dist(D[i].v, D[j].v) <= 2 * Rs:
                        parent = (D[i], D[j])
                        x = (D[i].v[0] + D[j].v[0]) / 2
                        y = (D[i].v[1] + D[j].v[1]) / 2
                        z = (D[i].v[2] + D[j].v[2]) / 2
                        D[i].intersections.append(IntersectionPoint((x, y, z), parent))
                        D[i].intersections.append(IntersectionPoint((x, y, z), parent))

    for Di in D:
        if len(Di.intersections) > 0:
            for point in Di.intersections:
                for Dj in D:
                    if point.is_cover(Dj):
                        point.cover.append(Dj)
                point.cover.sort(key=lambda x: x.index)
        else:
            Di.alone = True
            Di.intersections.append(IntersectionPoint(random_point_in_sphere(Di.v, Rs), Di))
            Di.intersections.append(IntersectionPoint(random_point_in_sphere(Di.v, Rs), Di))
            for point in Di.intersections:
                point.cover.append(Di)

        Di.find_best_point()

    Regions = []  # contain the intersections
    Regions_cover = []  # contain the sphere list that point in Regions covers
    Regions_cover_index = []  # contain the index of the corresponding sphere in Region_cover
    for Di in D:
        if Di.best_point[0].cover not in Regions_cover:
            Regions.append(Di.best_point)
            Regions_cover.append(Di.best_point[0].cover)

    for i in range(len(Regions_cover)):
        Regions_cover_index.append([])
        for j in range(len(Regions_cover[i])):
            Regions_cover_index[i].append(Regions_cover[i][j].index)

    Q = [T[i].q for i in range(len(T))]

    x = solve(n, Regions_cover_index, Q)

    S = []

    for i in range(len(Regions)):
        A = Regions[i][0].v
        B = Regions[i][1].v
        for j in range(x[i]):
            vector = (B[0] - A[0], B[1] - A[1], B[2] - A[2])
            t = random()
            sensor = [A[0] + t * vector[0], A[1] + t * vector[1], A[2] + t * vector[2]]
            tempS = Sensor(sensor, Rs, [])
            S.append(tempS)
    return S

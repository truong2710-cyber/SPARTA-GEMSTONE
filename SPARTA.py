from random import *
from math import *

from CONSTANT import *

from numpy import sqrt, dot, cross
from numpy.linalg import norm


# Contains the logic for vanilla SPARTA

# Find the intersection of three spheres
# P1,P2,P3 are the centers, r1,r2,r3 are the radii       
# Implementaton based on Wikipedia Trilateration article.                              
def trilaterate(P1, P2, P3, r1, r2, r3):
    try:
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
    except:
        return False, False


class IntersectionPoint(object):
    def __init__(self, v, parent):
        self.v = v
        self.parent = parent
        self.cover = []

    def is_cover(self, Sphere):
        if Sphere not in self.cover:
            if dist(self.v, Sphere.v) <= Sphere.R or Sphere in self.parent:
                return True

        return False

    def is_remove(self, rD):
        if len(self.parent) == 3:
            if self.parent[0] in rD or self.parent[1] in rD or self.parent[2] in rD:
                return True
        if len(self.parent) == 2:
            if self.parent[0] in rD or self.parent[1] in rD:
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


def SPARTA(T, Rs):
    """
    Contains the logic of SPARTA.
    @param T: Target set
    @param Rs: sensing radius
    @return: Sensor set
    """

    n = len(T)
    D = [Sphere(T[i], Rs, i) for i in range(n)]  # set of Sphere
    D.sort(key=lambda x: x.q)
    S = []  # set of sensor

    intersection_points = []

    # calc intersection points
    # find triad
    triad = []
    for i in range(n - 2):
        for j in range(i + 1, n - 1):
            for k in range(j + 1, n):
                p1, p2 = trilaterate(D[i].v, D[j].v, D[k].v, Rs, Rs, Rs)
                if p1 and p2:
                    parent = (D[i], D[j], D[k])
                    intersection_points.append(IntersectionPoint(p1, parent))
                    intersection_points.append(IntersectionPoint(p2, parent))
                    triad += list(parent)

    # find pair
    for i in range(n - 1):
        for j in range(i + 1, n):
            if dist(D[i].v, D[j].v) <= 2 * Rs:
                parent = (D[i], D[j])
                x = (D[i].v[0] + D[j].v[0]) / 2
                y = (D[i].v[1] + D[j].v[1]) / 2
                z = (D[i].v[2] + D[j].v[2]) / 2
                intersection_points.append(IntersectionPoint((x, y, z), parent))
                intersection_points.append(IntersectionPoint((x, y, z), parent))

    # calc point cover by intersection_points
    for point in intersection_points:
        for Di in D:
            if point.is_cover(Di):
                point.cover.append(Di)

    # calc number of sensor
    while len(D) != 0:
        # add Q sensors to Sphere that don't intersect with any other Sphere
        if len(intersection_points) == 0:

            for Di in D:
                for j in range(Di.q):
                    xi, yi, zi = Di.v
                    t = uniform(0, 2 * pi)
                    a = random()
                    if a > 0.5:
                        a -= 0.001
                    x, y, z = cos(t) * a * Rs + xi, sin(t) * a * Rs + yi, zi
                    sensor = (x, y, z)
                    tempS = Sensor(sensor, Rs, [Di.T])
                    S.append(tempS)
                    Di.T.Sensors.append(S[-1])

            D = []

        # calc number of Sphere covered and index of that Sphere
        else:
            # sort set of intersection points in descending order of number of Target covered
            intersection_points.sort(reverse=True, key=lambda x: len(x.cover))

            # point A
            A = intersection_points[0]
            x1, y1, z1 = A.v

            for i in range(1, len(intersection_points)):
                if intersection_points[i].cover == A.cover:
                    # point B
                    x2, y2, z2 = intersection_points[i].v
                    break

            # add Q sensors to S
            A.cover.sort(key=lambda x: x.q)
            minq = A.cover[0].q
            for i in range(minq):
                # place random
                # a = random()
                # x = x1 + a*(x2-x1)
                # y = y1 + a*(y2-y1)

                # place evenly

                x = x1 + (i + 1) * (x2 - x1) / (minq + 1)
                y = y1 + (i + 1) * (y2 - y1) / (minq + 1)
                z = z1 + (i + 1) * (z2 - z1) / (minq + 1)

                sensor = (x, y, z)
                tempS = Sensor(sensor, Rs, [])
                S.append(tempS)

                for j in range(len(A.cover)):
                    A.cover[j].T.Sensors.append(S[-1])

                    S[-1].Targets.append(A.cover[j].T)

            rD = []

            for i in range(len(A.cover)):
                A.cover[i].q -= minq

                if A.cover[i].q <= 0:
                    rD.append(A.cover[i])

            # remove sastified Sphere
            i = 0
            while i < len(intersection_points):
                if intersection_points[i].is_remove(rD):
                    intersection_points.pop(i)
                    i -= 1
                else:
                    intersection_points[i].remove_cover(rD)
                i += 1

            for r in rD:
                D.remove(r)

    return S
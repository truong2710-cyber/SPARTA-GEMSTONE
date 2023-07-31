from math import dist


def FCSA(Base, S, Rc):
    Rn = []
    for i in range(len(S)):
        P1 = S[i].v
        P2 = Base.v
        c = dist(S[i].v, Base.v)
        add = int((c - 1) // (Rc))

        for j in range(add):
            x = P1[0] + (j + 1) * (P2[0] - P1[0]) / (add + 1)
            y = P1[1] + (j + 1) * (P2[1] - P1[1]) / (add + 1)
            z = P1[2] + (j + 1) * (P2[2] - P1[2]) / (add + 1)

            sensor = (x, y, z)
            Rn.append(sensor)

    return Rn

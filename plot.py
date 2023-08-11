import os

import matplotlib.pyplot as plt
import numpy as np


def plot(data_asc, targets, sensors, relays, base, conn, file_name='./result.pdf'):
    ax = plt.figure(figsize=(20, 20)).add_subplot(projection='3d')

    def scatter(Points, c, marker, name, s):
        try:
            x, y, z = zip(*[Point.v for Point in Points])
            ax.scatter(x, y, z, c=c, marker=marker, label=name, s=s, alpha=1)
        except:
            x, y, z = zip(*[Point for Point in Points])
            ax.scatter(x, y, z, c=c, marker=marker, label=name, s=s, alpha=1)

    def plot_sphere(center, radius, ax):
        # Create a meshgrid of points within the sphere
        theta = np.linspace(0, 2 * np.pi, 100)
        phi = np.linspace(0, np.pi, 100)
        theta, phi = np.meshgrid(theta, phi)

        x = center[0] + radius * np.sin(phi) * np.cos(theta)
        y = center[1] + radius * np.sin(phi) * np.sin(theta)
        z = center[2] + radius * np.cos(phi)

        # plot the sphere
        ax.plot_surface(x, y, z, color='b', alpha=0.1)

    scatter(targets, c='r', marker='*', name='Target', s=100)
    scatter(sensors, c='g', marker='o', name='Sensor', s=60)
    scatter(relays, c='b', marker='o', name='Relay node', s=60)

    ax.scatter(*base.v, c='g', marker='^', label='Base station', s=200)

    for c in conn:
        P1 = c[0].v
        P2 = c[1].v
        P = zip(P1, P2)
        plt.plot(*P, c='green')

    _x = [25 * i for i in range(len(data_asc))]
    _y = [25 * i for i in range(len(data_asc))]
    _xx, _yy = np.meshgrid(_x, _y)
    x, y = _xx.ravel(), _yy.ravel()

    top = []

    bottom = np.zeros_like(top)
    width = depth = 25

    minx = []
    maxx = []

    for i in range(len(data_asc)):
        minx.append(min(data_asc[i]))
        maxx.append(max(data_asc[i]))

    for i in range(len(data_asc)):
        for j in range(len(data_asc[i])):
            top.append(data_asc[i][j] - min(minx))

    bottom = [min(minx) for i in range(len(top))]
    # ax.bar3d(x, y, bottom, width, depth, top, shade=True, alpha=0.01)

    ax.set_xlabel('X', fontsize=20, labelpad=14)
    ax.set_ylabel('Y', fontsize=20, labelpad=24)
    ax.set_zlabel('Z', fontsize=20, labelpad=18)
    ax.tick_params(axis='x', labelsize=20)
    ax.tick_params(axis='y', labelsize=20, pad=10)
    ax.tick_params(axis='z', labelsize=20, pad=12)
    plt.legend(fontsize=20)
    # ax.axis('equal')
    if os.path.isfile(file_name):
        os.remove(file_name)
    plt.savefig(file_name)
    # plt.show()
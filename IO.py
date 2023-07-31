import os.path
from random import *
from CONSTANT import *

seed(random_seed)


def Import_data(H, data=2, n=100, Rs=40, Rc=80, Qmax=10, change=1):
    '''

    @param H: size of the AoI (HxH)
    @param data: index of the dataset (start from 1)
    @param n: Number of target (start)
    @param Rs: Sensing radius (start)
    @param Rc: Communication radius (start)
    @param Qmax: Q max (start)
    @param change: index of the scenario (1: change n, 2: change Rs, 3: change Q max, 4: change Rc)
    @return: The dataset config, the target set for each case, vector Q for each case, dataset name, scenario index (from 0)
    '''
    global n_default , Rs_default, Rc_default , Qmax_default

    file = ["bacgiang", "hanoi", "lamdong", "sonla", "thaibinh"]
    Dataset = [[[n + n_step * i, Rs, Rc, Qmax] for i in range(dataset_num)],   # change n
               [[n, Rs + Rs_step * i, Rc, Qmax] for i in range(dataset_num)],  # change Rs
               [[n, Rs, Rc, Qmax + Qmax_step * i] for i in range(dataset_num)],# change Qmax
               [[n, Rs, Rc + Rc_step * i, Qmax] for i in range(dataset_num)]]  # change Rc

    file = file[data - 1]

    with open(f"Data/{file}.asc", "r") as f:
        f.readline()
        f.readline()
        xllcorner = float(f.readline()[9:-1])
        yllcorner = float(f.readline()[9:-1])
        cellsize = float(f.readline()[8:-1])
        NODATA_value = f.readline()
        data_asc = f.readlines()
        data_asc[0] = data_asc[0][13:]
        data_asc[0] = list(map(float, data_asc[0].split()))
        for i in range(1, len(data_asc)):
            data_asc[i] = list(map(float, data_asc[i].split()))
            data_asc[i - 1].append(data_asc[i].pop(0))
        data_asc.pop()
        cell = int(H // 25)
        data_asc = data_asc[-cell:]
        for i in range(len(data_asc)):
            data_asc[i] = data_asc[i][:cell]

    Dataset = Dataset[change - 1]

    Targets, Qs = place_random(Dataset, data_asc, change)

    return Dataset, Targets, Qs, file, change - 1, data_asc


def place_random(Dataset, data_asc, change):
    if change == 1:
        Targets = []
        Qs = []
        for j in range(len(Dataset)):
            n = Dataset[j][0]
            T = []

            for k in range(n):
                x, y = random() * H, random() * H
                z = data_asc[int(x // 25)][int(y // 25)]
                T.append([x, y, z])

            Qmax = Dataset[j][3]
            Q = [randint(1, Qmax) for _ in range(n)]

            Qs.append(Q)
            Targets.append(T.copy())

    elif change == 2 or change == 4:
        Targets = []
        Qs = []

        n = Dataset[0][0]
        T = []
        for k in range(n):
            x, y = random() * H, random() * H
            z = data_asc[int(x // 25)][int(y // 25)]
            T.append([x, y, z])

        Qmax = Dataset[0][3]
        Q = [randint(1, Qmax) for _ in range(n)]

        for j in range(len(Dataset)):
            Qs.append(Q.copy())
            Targets.append(T.copy())

    elif change == 3:
        Targets = []
        Qs = []
        n = Dataset[0][0]
        T = []
        for k in range(n):
            x, y = random() * H, random() * H
            z = data_asc[int(x // 25)][int(y // 25)]
            T.append([x, y, z])

        for j in range(len(Dataset)):
            Qmax = Dataset[j][3]
            Q = [randint(1, Qmax) for _ in range(n)]
            Qs.append(Q)
            Targets.append(T.copy())

    return Targets, Qs


def exportDataCov(average_S, average_runtimeCov, Dataset, file, name, H, change):
    n = Dataset[0][0]
    Rs = Dataset[0][1]
    Q = Dataset[0][3]
    changes = ["n", "Rs", 'Qmax', 'Rc']
    assert change != 3, "Cannot change Rc in Phase I!"
    if not os.path.exists(f"Result/{name}/{file}"):
        os.makedirs(f"Result/{name}/{file}")
    with open(f"Result/{name}/{file}/change {changes[change]} n{n} Rs{Rs} Q{Q} H{H} data.txt", "w") as f:
        if change == 0:
            f.write("changing n\n")
            for i in range(dataset_num):
                string = f'n = {Dataset[i][0]}, s1-1-{i + 1}, {average_S["n"][i]}, {average_runtimeCov["n"][i]}\n'
                f.write(string)
        if change == 1:
            f.write("changing Rs\n")
            for i in range(dataset_num):
                string = f'Rs = {Dataset[i][1]}, s1-2-{i + 1}, {average_S["Rs"][i]}, {average_runtimeCov["Rs"][i]}\n'
                f.write(string)
        if change == 2:
            f.write("changing Qmax\n")
            for i in range(dataset_num):
                string = f'Qmax = {Dataset[i][3]}, s1-3-{i + 1}, {average_S["Q"][i]}, {average_runtimeCov["Q"][i]}\n'
                f.write(string)


def exportDataCon(average_Rn, average_runtimeCon, Dataset, file, name, H, change):
    n = Dataset[0][0]
    Rs = Dataset[0][1]
    Rc = Dataset[0][2]
    Q = Dataset[0][3]
    changes = ["n", "Rs", 'Qmax', 'Rc']
    assert change != 1, "Cannot change Rs in Phase II!"
    if not os.path.exists(f"Result/{name}/{file}"):
        os.makedirs(f"Result/{name}/{file}")
    with open(f"Result/{name}/{file}/change {changes[change]} n{n} Rc{Rc} Q{Q} H{H} data.txt", "a") as f:
        if change == 0:
            f.write("changing n\n")
            for i in range(dataset_num):
                string = f'n = {Dataset[i][0]}, s2-1-{i + 1}, {average_Rn["n"][i]}, {average_runtimeCon["n"][i]}\n'
                f.write(string)
        if change == 3:
            f.write("changing Rc\n")
            for i in range(dataset_num):
                string = f'Rc = {Dataset[i][2]}, s2-2-{i + 1}, {average_Rn["Rc"][i]}, {average_runtimeCon["Rc"][i]}\n'
                f.write(string)
        if change == 2:
            f.write("changing Qmax\n")
            for i in range(dataset_num):
                string = f'Qmax = {Dataset[i][3]}, s2-3-{i + 1}, {average_Rn["Q"][i]}, {average_runtimeCon["Q"][i]}\n'
                f.write(string)


def exportDataBoth(average_S, average_Rn, average_runtime, Dataset, file, name, H, change):
    n = Dataset[0][0]
    Rs = Dataset[0][1]
    Rc = Dataset[0][2]
    Q = Dataset[0][3]
    changes = ["n", "Rs", 'Qmax', 'Rc']

    if not os.path.exists(f"Result/{name}/{file}"):
        os.makedirs(f"Result/{name}/{file}")
    with open(f"Result/{name}/{file}/change {changes[change]} n{n} Rs{Rs} Rc{Rc} Q{Q} H{H} data.txt", "a") as f:
        if change == 0:
            f.write("changing n\n")
            for i in range(dataset_num):
                string = f'n = {Dataset[i][0]}, s3-1-{i + 1}, {average_S["n"][i]}, {average_Rn["n"][i]}, {average_runtime["n"][i]}\n'
                f.write(string)
        if change == 1:
            f.write("changing Rs\n")
            for i in range(dataset_num):
                string = f'Rs = {Dataset[i][1]}, s3-2-{i + 1}, {average_S["Rs"][i]}, {average_Rn["Rs"][i]}, {average_runtime["Rs"][i]}\n'
                f.write(string)
        if change == 3:
            f.write("changing Rc\n")
            for i in range(dataset_num):
                string = f'Rc = {Dataset[i][2]}, s3-3-{i + 1}, {average_S["Rc"][i]}, {average_Rn["Rc"][i]}, {average_runtime["Rc"][i]}\n'
                f.write(string)
        if change == 2:
            f.write("changing Qmax\n")
            for i in range(dataset_num):
                string = f'Qmax = {Dataset[i][3]}, s3-4-{i + 1}, {average_S["Q"][i]}, {average_Rn["Q"][i]}, {average_runtime["Q"][i]}\n'
                f.write(string)
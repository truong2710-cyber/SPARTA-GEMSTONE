import timeit
from tqdm import tqdm
from CMFA import *
from GEMSTONE import GEMSTONE
from GLA import GLA
from SPARTA_CP import SPARTA_CP
from plot import plot
from IO import *

seed(random_seed)


def main(data, n, Rs, Rc, Qmax, change):
    global H
    Dataset, Targets, Qs, file, i, data_asc = Import_data(H, data, n, Rs, Rc, Qmax, change)
    base = Base([0, 0, data_asc[0][0]])

    average_s = {}
    average_runtime = {}
    average_rn = {}

    average_s['n'] = [0] * dataset_num
    average_rn['n'] = [0] * dataset_num
    average_runtime['n'] = [0] * dataset_num
    average_s['Rs'] = [0] * dataset_num
    average_rn['Rs'] = [0] * dataset_num
    average_runtime['Rs'] = [0] * dataset_num
    average_s['Q'] = [0] * dataset_num
    average_rn['Q'] = [0] * dataset_num
    average_runtime['Q'] = [0] * dataset_num
    average_s['Rc'] = [0] * dataset_num
    average_rn['Rc'] = [0] * dataset_num
    average_runtime['Rc'] = [0] * dataset_num

    change = ["n", "Rs", "Q", "Rc"]

    for j in tqdm(range(len(Dataset))):  # len(Dataset)
        for run in tqdm(range(data_num)):  # data_num
            n = Dataset[j][0]
            Rs = Dataset[j][1]
            Rc = Dataset[j][2]
            Qmax = max(Qs[j])
            Rcl = 100

            T = [Target(Targets[j][k], Qs[j][k], []) for k in range(n)]

            starttime = timeit.default_timer()
            S = SPARTA_CP(T, Rs)
            # S = GLA(T, Rs)
            # Rn, conn = CMFA(base, T, S, Rc, Rcl, Rs, Qmax)
            Rn, conn = GEMSTONE(base, T, Rc)

            average_s[change[i]][j] += (len(S))
            average_rn[change[i]][j] += (len(Rn))
            endtime = timeit.default_timer()

            average_runtime[change[i]][j] += (endtime - starttime)

        average_s[change[i]][j] = round(average_s[change[i]][j] / data_num)
        average_rn[change[i]][j] = round(average_rn[change[i]][j] / data_num)
        average_runtime[change[i]][j] = round(average_runtime[change[i]][j] / data_num, 5)

        exportDataBoth(average_s, average_rn, average_runtime, Dataset, file, "SPARTA_CP_GEMSTONE", H, i)
        plot(data_asc, T, S, Rn, base, conn)


if __name__ == "__main__":
    main(data=4, n=400, Rs=40, Rc=80, Qmax=10, change=1)

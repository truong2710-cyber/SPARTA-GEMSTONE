import argparse
import timeit
from tqdm import tqdm
from CMFA import *
from GEMSTONE import GEMSTONE
from GLA import GLA
from SPARTA_CP import SPARTA_CP
from plot import plot
from IO import *
import CONSTANT

seed(CONSTANT.random_seed)


def two_element_list(string):
    """
    Custom type for argparse that takes a comma-separated string and returns
    a list with two elements.
    """
    elements = string.split(',')
    if len(elements) != 2:
        raise argparse.ArgumentTypeError("List must have exactly 2 elements")
    return [int(elements[0]), int(elements[1])]

parser = argparse.ArgumentParser(description='Model input')
parser.add_argument('--N', metavar='N', type=int, dest="num_target",
                    help='number of targets', default=400)
parser.add_argument('--qm', metavar='q_max', type=int, dest="q_max",
                    help='maximum q of all the targets', default=10)
parser.add_argument('--rs', metavar='r_s', type=float, dest="r_s",
                    help='sensing radius', default=40)
parser.add_argument('--rc', metavar='r_c', type=float, dest="r_c",
                    help='communication radius', default=80)
parser.add_argument('--rcl', metavar='r_cl', type=float, dest="r_cl",
                    help='cluster radius', default=80)
parser.add_argument('--ra', metavar='rand_q', type=bool, dest="rand_q",
                    help='random q or not', default=True)
parser.add_argument('--d', metavar='dataset_name', type=str, dest="dataset",
                    help='dataset name', default='sonla', choices=["bacgiang", "hanoi", "lamdong", "sonla", "thaibinh"])
parser.add_argument('--w', metavar='width', type=float, dest="width",
                    help='area width (=height)', default=2000)
parser.add_argument('--b', metavar='base', type=two_element_list, dest="base",
                    help='base station location in xy-coordinate', default=[0, 0])
parser.add_argument('--ch', metavar='change', type=str, dest="change",
                    help='which factor to change', default="n", choices=['n', 'Rs', 'Q', 'Rc'])
parser.add_argument('--s', metavar='step', type=int, dest="step",
                    help='step of the change', default=15)
parser.add_argument('--ns', metavar='num_step', type=int, dest="num_step",
                    help='how many steps to take', default=6)
parser.add_argument('--nr', metavar='num_run', type=int, dest="num_run",
                    help='how many runs in one data config', default=20)
parser.add_argument('--p1', metavar='algo_p1', type=str, dest="algo_p1",
                    help='which algorithm to use in phase I', default="sparta_cc", choices=['sparta', 'sparta_cc', 'sparta_cp'])
parser.add_argument('--p2', metavar='algo_p2', type=str, dest="algo_p2",
                    help='which algorithm to use in phase II', default="gemstone", choices=['gemstone', 'cmfa'])
args = parser.parse_args()
    

def main(args):
    # global H
    change = ["n", "Rs", "Q", "Rc"]
    if args.change == 'n':
        CONSTANT.n_step = args.step
    if args.change == 'Rs':
        CONSTANT.Rs_step = args.step
    if args.change == 'Q':
        CONSTANT.Qmax_step = args.step
    if args.change == 'Rc':
        CONSTANT.Rc_step = args.step

    CONSTANT.dataset_num = args.num_step
    CONSTANT.data_num = args.num_run
    CONSTANT.H = args.width
    
    Dataset, Targets, Qs, file, factor_idx, data_asc = Import_data(args.width, args.dataset, args.num_target, args.r_s, args.r_c, args.q_max, change.index(args.change)+1)
    base = CONSTANT.Base([args.base[0], args.base[1], data_asc[args.base[0]//25][args.base[1]//25]])

    average_s = {}
    average_runtime = {}
    average_rn = {}

    average_s['n'] = [0] * CONSTANT.dataset_num
    average_rn['n'] = [0] * CONSTANT.dataset_num
    average_runtime['n'] = [0] * CONSTANT.dataset_num
    average_s['Rs'] = [0] * CONSTANT.dataset_num
    average_rn['Rs'] = [0] * CONSTANT.dataset_num
    average_runtime['Rs'] = [0] * CONSTANT.dataset_num
    average_s['Q'] = [0] * CONSTANT.dataset_num
    average_rn['Q'] = [0] * CONSTANT.dataset_num
    average_runtime['Q'] = [0] * CONSTANT.dataset_num
    average_s['Rc'] = [0] * CONSTANT.dataset_num
    average_rn['Rc'] = [0] * CONSTANT.dataset_num
    average_runtime['Rc'] = [0] * CONSTANT.dataset_num 

    for j in tqdm(range(len(Dataset))):  # len(Dataset)
        for run in tqdm(range(CONSTANT.data_num)):  # data_num
            n = Dataset[j][0]
            Rs = Dataset[j][1]
            Rc = Dataset[j][2]
            Qmax = max(Qs[j])
            Rcl = 100

            T = [CONSTANT.Target(Targets[j][k], Qs[j][k], []) for k in range(n)]

            starttime = timeit.default_timer()

            if args.algo_p1 == "sparta_cp":
                S = SPARTA_CP(T, Rs)
            elif args.algo_p1 == "sparta_cc":
                S = SPARTA_CC(T, Rs)
            elif args.algo_p1 == "sparta":
                S = SPARTA(T, Rs)
    
            if args.algo_p2 == "gemstone":
                Rn, conn = GEMSTONE(base, T, Rc)
            if args.algo_p2 == "cmfa":
                assert Rcl >= 2 * Rs, "Invalid cluster radius!"
                Rn, conn = CMFA(base, T, S, Rc, Rcl, Rs, Qmax)

            average_s[change[factor_idx]][j] += (len(S))
            average_rn[change[factor_idx]][j] += (len(Rn))
            endtime = timeit.default_timer()

            average_runtime[change[factor_idx]][j] += (endtime - starttime)

        average_s[change[factor_idx]][j] = round(average_s[change[factor_idx]][j] / CONSTANT.data_num)
        average_rn[change[factor_idx]][j] = round(average_rn[change[factor_idx]][j] / CONSTANT.data_num)
        average_runtime[change[factor_idx]][j] = round(average_runtime[change[factor_idx]][j] / CONSTANT.data_num, 5)
        
    exportDataBoth(average_s, average_rn, average_runtime, Dataset, file, args.algo_p1+"_"+args.algo_p2, args.width, factor_idx)
        # plot(data_asc, T, S, Rn, base, conn)


if __name__ == "__main__":
    main(args)

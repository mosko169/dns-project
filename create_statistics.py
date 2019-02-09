import os
import csv
import sys
import matplotlib.pyplot as plt
import numpy as np


def num_list_to_cdf(num_list):
    num_list.sort()
    accumulate_percents = []

    for i in range(max(num_list)+1):
        curr_count = num_list.count(i)
        curr_perc = float(curr_count) / len(num_list)
        if len(accumulate_percents) == 0:
            accumulate_percents.append(curr_perc)
        else:
            accumulate_percents.append(curr_perc + accumulate_percents[-1])

    return accumulate_percents


def create_cdf_graph(cdf_list, output_path):
    data = np.arange(0, len(cdf_list)+1)
    y = np.array(cdf_list)

    fig, ax = plt.subplots()
    ax.set_facecolor('white')

    # https://matplotlib.org/api/_as_gen/matplotlib.axes.Axes.hlines.html
    ax.hlines(y=y, xmin=data[:-1], xmax=data[1:],
              color='red', zorder=1)

    # https://matplotlib.org/api/_as_gen/matplotlib.axes.Axes.vlines.html
    ax.vlines(x=data[1:-1], ymin=y[:-1], ymax=y[1:], color='red',
              linestyle='dashed', zorder=1)
    ax.scatter(data[0:-1], y, color='red', s=18, zorder=2)
    ax.grid(False)

    ax.set_xlim(data[0], data[-1])
    ax.set_ylim([-0.01, 1.01])

    plt.savefig(output_path)


def get_result(file_path):
    ns_cnt = list()
    glue_cnt = list()
    out_of_bailiwick_cnt = list()
    f = open(file_path, "r")
    next(f)
    reader = csv.reader(f)
    for r in reader:
        ns_cnt.append(int(r[1]))
        glue_cnt.append(int(r[2]))
        out_of_bailiwick_cnt.append(int(r[3]))

    return ns_cnt, glue_cnt, out_of_bailiwick_cnt


def create_ns_histogram(list, output_dir):
    plt.hist(list, bins=max(list), color='#0504aa')
    plt.xlabel("Number of ns records")
    plt.ylabel("Count of occurrence")
    plt.title("Distribution of ns records count")
    plt.savefig(os.path.join(output_dir, "NS_HIST.png"))


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} input_file [out_dir]")
        print("This program creates an histogram and cdf file relevant to our study")
        print("if no output dir was given, current one will be used")
        sys.exit(0)
    elif len(sys.argv) == 2:
        output_dir = os.getcwd()
    else:
        output_dir = sys.argv[2]

    ns_cnt, glue_cnt, out_of_bailiwick_cnt = get_result(sys.argv[1])

    create_ns_histogram(ns_cnt, output_dir)
    for name, cnt_list in {"NS_CDF": ns_cnt, "GLUE_CDF": glue_cnt, "OUT_OF_BAILWICK": out_of_bailiwick_cnt}.items():
        create_cdf_graph(num_list_to_cdf(cnt_list), os.path.join(output_dir, name))


if __name__ == "__main__":
    main()

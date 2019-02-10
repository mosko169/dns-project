import os
import csv
import matplotlib.pyplot as plt
import numpy as np
import argparse


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


def create_cdf_graph(cdf_list, labels, output_path):
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
    plt.xlabel(labels[0])
    plt.ylabel(labels[1])
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


def create_ns_histogram(counters_list, output_dir):
    plt.figure(figsize=(12, 8))
    plt.hist(counters_list, bins=max(counters_list), color='#0504aa')
    plt.xlabel("Number of ns records")
    plt.ylabel("Count of occurrence")
    plt.title("Distribution of ns records count")
    values = list(set(counters_list))
    ax = plt.gca()
    ax.xaxis.set_ticks(range(0, max(values), 2))
    ax.set_xlim(auto=True)
    plt.savefig(os.path.join(output_dir, "NS_HIST.png"))


def main():
    parser = argparse.ArgumentParser(description='Output:\n' +
                                                 'NS_HIST.png - Nameservers histogram\n' +
                                                 'NS_CDF.png - Nameservers CDF\n' +
                                                 'GLUE_CDF.png - Glue records CDF\n' +
                                                 'OUT_OF_BAILIWICK_CDF.png - Out-of-bailiwick Glue records CDF', formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-counters_file",
                        help="path of output file of ns.py script (contains the counters gathered on the given domains)",
                        required=True)
    parser.add_argument("-output_dir", help="path of directory to output the plots", required=False)
    args = parser.parse_args()
    if args.output_dir:
        output_dir = args.output_dir
    else:
        output_dir = os.getcwd()

    ns_cnt, glue_cnt, out_of_bailiwick_cnt = get_result(args.counters_file)
    create_ns_histogram(ns_cnt, output_dir)
    for stat in [("NS_CDF",("Number of name servers", "Percentage"), ns_cnt), ("GLUE_CDF", ("Number of glue records", "Percentage"), glue_cnt), ("OUT_OF_BAILIWICK", ("Number of Out-of-bailiwick glue records", "Percentage"), out_of_bailiwick_cnt)]:
        create_cdf_graph(num_list_to_cdf(stat[2]), stat[1], os.path.join(output_dir, stat[0]))


if __name__ == "__main__":
    main()

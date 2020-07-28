"""
TrajectoriesAstar. Towards a human-like movements generator based on environmental features
Copyright (C) 2020  Alessandro Zonta (a.zonta@vu.nl)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import logging
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from scipy.stats import stats
import numpy as np

"""
The code will show all the result analysed together and plot the graphs as visible in the paper
It also compute some statistics on the data
"""
if __name__ == '__main__':
    logger = logging.getLogger("LoadTrajectories")
    logger.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(ch)
    logger.info("Starting script")

    # get all the h5 files
    path_to_read = "/Users/alessandrozonta/PycharmProjects/astar/output/"
    astar_attraction = pd.read_hdf("{}/test_normal_data".format(path_to_read))
    test_with_pd_0_1_2_data = pd.read_hdf("{}/test_with_pd_0_1_2_data".format(path_to_read))
    test_with_pd_0_1_data = pd.read_hdf("{}/test_with_pd_0_1_data".format(path_to_read))
    test_with_pd_0_2_data = pd.read_hdf("{}/test_with_pd_0_2_data".format(path_to_read))
    test_with_pd_0_data = pd.read_hdf("{}/test_with_pd_0_data".format(path_to_read))
    test_with_pd_1_2_data = pd.read_hdf("{}/test_with_pd_1_2_data".format(path_to_read))
    test_with_pd_1_data = pd.read_hdf("{}/test_with_pd_1_data".format(path_to_read))
    test_with_pd_2_data = pd.read_hdf("{}/test_with_pd_2_data".format(path_to_read))
    astar = pd.read_hdf("{}/normal_astar".format(path_to_read))

    # Declare a list that is to be converted into a column
    list_to_add_astar_attraction = ["aa" for _ in range(astar_attraction.shape[0])]
    list_to_add_test_with_pd_0_1_2_data = ["aa012" for _ in range(test_with_pd_0_1_2_data.shape[0])]
    list_to_add_test_with_pd_0_1_data = ["aa01" for _ in range(test_with_pd_0_1_data.shape[0])]
    list_to_add_test_with_pd_0_2_data = ["aa02" for _ in range(test_with_pd_0_2_data.shape[0])]
    list_to_add_test_with_pd_0_data = ["aa0" for _ in range(test_with_pd_0_data.shape[0])]
    list_to_add_test_with_pd_1_2_data = ["aa12" for _ in range(test_with_pd_1_2_data.shape[0])]
    list_to_add_test_with_pd_1_data = ["aa1" for _ in range(test_with_pd_1_data.shape[0])]
    list_to_add_test_with_pd_2_data = ["aa2" for _ in range(test_with_pd_2_data.shape[0])]
    list_to_add_astar = ["a" for _ in range(astar.shape[0])]


    # add list to dataframes
    astar_attraction['source'] = list_to_add_astar_attraction
    test_with_pd_0_1_2_data['source'] = list_to_add_test_with_pd_0_1_2_data
    test_with_pd_0_1_data['source'] = list_to_add_test_with_pd_0_1_data
    test_with_pd_0_2_data['source'] =list_to_add_test_with_pd_0_2_data
    test_with_pd_0_data['source'] = list_to_add_test_with_pd_0_data
    test_with_pd_1_2_data['source'] = list_to_add_test_with_pd_1_2_data
    test_with_pd_1_data['source'] = list_to_add_test_with_pd_1_data
    test_with_pd_2_data['source'] = list_to_add_test_with_pd_2_data
    astar['source'] = list_to_add_astar


    frames = [astar, astar_attraction, test_with_pd_0_1_2_data, test_with_pd_0_1_data, test_with_pd_0_2_data,
              test_with_pd_0_data,
              test_with_pd_1_2_data, test_with_pd_1_data, test_with_pd_2_data]
    df = pd.concat(frames)
    df["fitness"] = df["fitness"] / 600
    df["direction"] = df["direction"] / 800
    df["no_overlapping"] = df["no_overlapping"] / 200

    small_dataset = df[["direction", "fitness", "no_overlapping", "source"]]
    small_dataset.columns = ['Directions', 'Fitness', "No_Overlapping", "Source"]

    reshaped = small_dataset.melt(id_vars=['Source'], value_vars=['No_Overlapping', 'Fitness', 'Directions'])
    reshaped.columns = ['Versions', 'Measurements', "Score"]
    sns.boxplot(x="Measurements", y="Score", hue="Versions", data=reshaped)
    sns.despine(offset=10, trim=True)
    plt.savefig("{}/combined_graph.pdf".format(path_to_read))
    plt.close()

    save_figure = True

    type_to_check = "total_length"
    #
    sns.distplot(df[df["source"] == "a"][type_to_check], label="a", kde=False, rug=True)
    sns.distplot(df[df["source"] == "aa"][type_to_check], label="aa", kde=False, rug=True)
    sns.distplot(df[df["source"] == "aa012"][type_to_check], label="aa012", kde=False, rug=True)
    sns.distplot(df[df["source"] == "aa01"][type_to_check], label="aa01", kde=False, rug=True)
    sns.distplot(df[df["source"] == "aa02"][type_to_check], label="aa02", kde=False, rug=True)
    sns.distplot(df[df["source"] == "aa0"][type_to_check], label="aa0", kde=False, rug=True)
    sns.distplot(df[df["source"] == "aa12"][type_to_check], label="aa12", kde=False, rug=True)
    sns.distplot(df[df["source"] == "aa1"][type_to_check], label="aa1", kde=False, rug=True)
    ax = sns.distplot(df[df["source"] == "aa2"][type_to_check], label="aa2", kde=False, rug=True)
    ax.set(xlabel='Total length')
    plt.legend()
    sns.despine(offset=10, trim=True)
    path_to_read = "/Users/alessandrozonta/PycharmProjects/astar/output/"
    if save_figure is True:
        plt.savefig("{}/total_length_astar.pdf".format(path_to_read))
    else:
        plt.show()
    plt.close()


    total = []
    total.append(stats.ks_2samp(df[df["source"] == "a"]['fitness'], df[df["source"] == "aa012"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "a"]['fitness'], df[df["source"] == "aa01"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "a"]['fitness'], df[df["source"] == "aa02"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "a"]['fitness'], df[df["source"] == "aa0"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "a"]['fitness'], df[df["source"] == "aa12"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "a"]['fitness'], df[df["source"] == "aa1"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "a"]['fitness'], df[df["source"] == "aa2"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "a"]['fitness'], df[df["source"] == "aa"]['fitness']).pvalue)

    # small p -> two different distributions

    logger.info(total)
    logger.info(np.mean(np.array(total)))
    logger.info(np.std(np.array(total)))

    total = []
    total.append(stats.ks_2samp(df[df["source"] == "aa"]['fitness'], df[df["source"] == "aa012"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa"]['fitness'], df[df["source"] == "aa01"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa"]['fitness'], df[df["source"] == "aa02"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa"]['fitness'], df[df["source"] == "aa0"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa"]['fitness'], df[df["source"] == "aa12"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa"]['fitness'], df[df["source"] == "aa1"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa"]['fitness'], df[df["source"] == "aa2"]['fitness']).pvalue)

    total.append(stats.ks_2samp(df[df["source"] == "aa012"]['fitness'], df[df["source"] == "aa"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa012"]['fitness'], df[df["source"] == "aa01"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa012"]['fitness'], df[df["source"] == "aa02"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa012"]['fitness'], df[df["source"] == "aa0"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa012"]['fitness'], df[df["source"] == "aa12"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa012"]['fitness'], df[df["source"] == "aa1"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa012"]['fitness'], df[df["source"] == "aa2"]['fitness']).pvalue)

    total.append(stats.ks_2samp(df[df["source"] == "aa01"]['fitness'], df[df["source"] == "aa"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa01"]['fitness'], df[df["source"] == "aa012"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa01"]['fitness'], df[df["source"] == "aa02"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa01"]['fitness'], df[df["source"] == "aa0"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa01"]['fitness'], df[df["source"] == "aa12"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa01"]['fitness'], df[df["source"] == "aa1"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa01"]['fitness'], df[df["source"] == "aa2"]['fitness']).pvalue)

    total.append(stats.ks_2samp(df[df["source"] == "aa02"]['fitness'], df[df["source"] == "aa"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa02"]['fitness'], df[df["source"] == "aa012"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa02"]['fitness'], df[df["source"] == "aa01"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa02"]['fitness'], df[df["source"] == "aa0"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa02"]['fitness'], df[df["source"] == "aa12"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa02"]['fitness'], df[df["source"] == "aa1"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa02"]['fitness'], df[df["source"] == "aa2"]['fitness']).pvalue)

    total.append(stats.ks_2samp(df[df["source"] == "aa0"]['fitness'], df[df["source"] == "aa"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa0"]['fitness'], df[df["source"] == "aa012"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa0"]['fitness'], df[df["source"] == "aa01"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa0"]['fitness'], df[df["source"] == "aa2"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa0"]['fitness'], df[df["source"] == "aa12"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa0"]['fitness'], df[df["source"] == "aa1"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa0"]['fitness'], df[df["source"] == "aa2"]['fitness']).pvalue)

    total.append(stats.ks_2samp(df[df["source"] == "aa12"]['fitness'], df[df["source"] == "aa"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa12"]['fitness'], df[df["source"] == "aa012"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa12"]['fitness'], df[df["source"] == "aa01"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa12"]['fitness'], df[df["source"] == "aa2"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa12"]['fitness'], df[df["source"] == "aa0"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa12"]['fitness'], df[df["source"] == "aa1"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa12"]['fitness'], df[df["source"] == "aa2"]['fitness']).pvalue)

    total.append(stats.ks_2samp(df[df["source"] == "aa1"]['fitness'], df[df["source"] == "aa"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa1"]['fitness'], df[df["source"] == "aa012"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa1"]['fitness'], df[df["source"] == "aa01"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa1"]['fitness'], df[df["source"] == "aa2"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa1"]['fitness'], df[df["source"] == "aa0"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa1"]['fitness'], df[df["source"] == "aa12"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa1"]['fitness'], df[df["source"] == "aa2"]['fitness']).pvalue)

    total.append(stats.ks_2samp(df[df["source"] == "aa2"]['fitness'], df[df["source"] == "aa"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa2"]['fitness'], df[df["source"] == "aa012"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa2"]['fitness'], df[df["source"] == "aa01"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa2"]['fitness'], df[df["source"] == "aa2"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa2"]['fitness'], df[df["source"] == "aa0"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa2"]['fitness'], df[df["source"] == "aa12"]['fitness']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa2"]['fitness'], df[df["source"] == "aa1"]['fitness']).pvalue)

    # small p -> two different distributions

    logger.info(total)
    logger.info(np.mean(np.array(total)))
    logger.info(np.std(np.array(total)))


    total = []
    total.append(stats.ks_2samp(df[df["source"] == "a"]['no_overlapping'], df[df["source"] == "aa012"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "a"]['no_overlapping'], df[df["source"] == "aa01"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "a"]['no_overlapping'], df[df["source"] == "aa02"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "a"]['no_overlapping'], df[df["source"] == "aa0"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "a"]['no_overlapping'], df[df["source"] == "aa12"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "a"]['no_overlapping'], df[df["source"] == "aa1"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "a"]['no_overlapping'], df[df["source"] == "aa2"]['no_overlapping']).pvalue)

    logger.info(total)
    logger.info(np.mean(np.array(total)))
    logger.info(np.std(np.array(total)))

    total = []
    total.append(stats.ks_2samp(df[df["source"] == "aa"]['no_overlapping'], df[df["source"] == "aa012"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa"]['no_overlapping'], df[df["source"] == "aa01"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa"]['no_overlapping'], df[df["source"] == "aa02"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa"]['no_overlapping'], df[df["source"] == "aa0"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa"]['no_overlapping'], df[df["source"] == "aa12"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa"]['no_overlapping'], df[df["source"] == "aa1"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa"]['no_overlapping'], df[df["source"] == "aa2"]['no_overlapping']).pvalue)

    total.append(stats.ks_2samp(df[df["source"] == "aa012"]['no_overlapping'], df[df["source"] == "aa"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa012"]['no_overlapping'], df[df["source"] == "aa01"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa012"]['no_overlapping'], df[df["source"] == "aa02"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa012"]['no_overlapping'], df[df["source"] == "aa0"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa012"]['no_overlapping'], df[df["source"] == "aa12"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa012"]['no_overlapping'], df[df["source"] == "aa1"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa012"]['no_overlapping'], df[df["source"] == "aa2"]['no_overlapping']).pvalue)

    total.append(stats.ks_2samp(df[df["source"] == "aa01"]['no_overlapping'], df[df["source"] == "aa"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa01"]['no_overlapping'], df[df["source"] == "aa012"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa01"]['no_overlapping'], df[df["source"] == "aa02"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa01"]['no_overlapping'], df[df["source"] == "aa0"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa01"]['no_overlapping'], df[df["source"] == "aa12"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa01"]['no_overlapping'], df[df["source"] == "aa1"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa01"]['no_overlapping'], df[df["source"] == "aa2"]['no_overlapping']).pvalue)

    total.append(stats.ks_2samp(df[df["source"] == "aa02"]['no_overlapping'], df[df["source"] == "aa"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa02"]['no_overlapping'], df[df["source"] == "aa012"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa02"]['no_overlapping'], df[df["source"] == "aa01"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa02"]['no_overlapping'], df[df["source"] == "aa0"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa02"]['no_overlapping'], df[df["source"] == "aa12"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa02"]['no_overlapping'], df[df["source"] == "aa1"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa02"]['no_overlapping'], df[df["source"] == "aa2"]['no_overlapping']).pvalue)

    total.append(stats.ks_2samp(df[df["source"] == "aa0"]['no_overlapping'], df[df["source"] == "aa"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa0"]['no_overlapping'], df[df["source"] == "aa012"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa0"]['no_overlapping'], df[df["source"] == "aa01"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa0"]['no_overlapping'], df[df["source"] == "aa2"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa0"]['no_overlapping'], df[df["source"] == "aa12"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa0"]['no_overlapping'], df[df["source"] == "aa1"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa0"]['no_overlapping'], df[df["source"] == "aa2"]['no_overlapping']).pvalue)

    total.append(stats.ks_2samp(df[df["source"] == "aa12"]['no_overlapping'], df[df["source"] == "aa"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa12"]['no_overlapping'], df[df["source"] == "aa012"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa12"]['no_overlapping'], df[df["source"] == "aa01"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa12"]['no_overlapping'], df[df["source"] == "aa2"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa12"]['no_overlapping'], df[df["source"] == "aa0"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa12"]['no_overlapping'], df[df["source"] == "aa1"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa12"]['no_overlapping'], df[df["source"] == "aa2"]['no_overlapping']).pvalue)

    total.append(stats.ks_2samp(df[df["source"] == "aa1"]['no_overlapping'], df[df["source"] == "aa"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa1"]['no_overlapping'], df[df["source"] == "aa012"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa1"]['no_overlapping'], df[df["source"] == "aa01"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa1"]['no_overlapping'], df[df["source"] == "aa2"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa1"]['no_overlapping'], df[df["source"] == "aa0"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa1"]['no_overlapping'], df[df["source"] == "aa12"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa1"]['no_overlapping'], df[df["source"] == "aa2"]['no_overlapping']).pvalue)

    total.append(stats.ks_2samp(df[df["source"] == "aa2"]['no_overlapping'], df[df["source"] == "aa"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa2"]['no_overlapping'], df[df["source"] == "aa012"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa2"]['no_overlapping'], df[df["source"] == "aa01"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa2"]['no_overlapping'], df[df["source"] == "aa2"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa2"]['no_overlapping'], df[df["source"] == "aa0"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa2"]['no_overlapping'], df[df["source"] == "aa12"]['no_overlapping']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa2"]['no_overlapping'], df[df["source"] == "aa1"]['no_overlapping']).pvalue)

    # small p -> two different distributions

    logger.info(total)
    logger.info(np.mean(np.array(total)))
    logger.info(np.std(np.array(total)))

    total = []
    total.append(stats.ks_2samp(df[df["source"] == "a"]['direction'], df[df["source"] == "aa012"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "a"]['direction'], df[df["source"] == "aa01"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "a"]['direction'], df[df["source"] == "aa02"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "a"]['direction'], df[df["source"] == "aa0"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "a"]['direction'], df[df["source"] == "aa12"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "a"]['direction'], df[df["source"] == "aa1"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "a"]['direction'], df[df["source"] == "aa2"]['direction']).pvalue)

    logger.info(total)
    logger.info(np.mean(np.array(total)))
    logger.info(np.std(np.array(total)))

    total = []
    total.append(stats.ks_2samp(df[df["source"] == "aa"]['direction'], df[df["source"] == "aa012"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa"]['direction'], df[df["source"] == "aa01"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa"]['direction'], df[df["source"] == "aa02"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa"]['direction'], df[df["source"] == "aa0"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa"]['direction'], df[df["source"] == "aa12"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa"]['direction'], df[df["source"] == "aa1"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa"]['direction'], df[df["source"] == "aa2"]['direction']).pvalue)

    logger.info(total)
    logger.info(np.mean(np.array(total)))
    logger.info(np.std(np.array(total)))

    total = []
    total.append(stats.ks_2samp(df[df["source"] == "aa012"]['direction'], df[df["source"] == "aa"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa012"]['direction'], df[df["source"] == "a"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa012"]['direction'], df[df["source"] == "aa01"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa012"]['direction'], df[df["source"] == "aa02"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa012"]['direction'], df[df["source"] == "aa0"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa012"]['direction'], df[df["source"] == "aa12"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa012"]['direction'], df[df["source"] == "aa1"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa012"]['direction'], df[df["source"] == "aa2"]['direction']).pvalue)

    logger.info(total)
    logger.info(np.mean(np.array(total)))
    logger.info(np.std(np.array(total)))

    total = []
    total.append(stats.ks_2samp(df[df["source"] == "aa12"]['direction'], df[df["source"] == "aa012"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa12"]['direction'], df[df["source"] == "aa01"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa12"]['direction'], df[df["source"] == "aa02"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa12"]['direction'], df[df["source"] == "aa0"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa12"]['direction'], df[df["source"] == "aa"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa12"]['direction'], df[df["source"] == "aa1"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa12"]['direction'], df[df["source"] == "aa2"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa12"]['direction'], df[df["source"] == "a"]['direction']).pvalue)

    logger.info(total)
    logger.info(np.mean(np.array(total)))
    logger.info(np.std(np.array(total)))

    total = []
    total.append(stats.ks_2samp(df[df["source"] == "aa"]['direction'],
                                df[df["source"] == "aa012"]['direction']).pvalue)
    total.append(
        stats.ks_2samp(df[df["source"] == "aa"]['direction'], df[df["source"] == "aa01"]['direction']).pvalue)
    total.append(
        stats.ks_2samp(df[df["source"] == "aa"]['direction'], df[df["source"] == "aa02"]['direction']).pvalue)
    total.append(
        stats.ks_2samp(df[df["source"] == "aa"]['direction'], df[df["source"] == "aa0"]['direction']).pvalue)
    total.append(
        stats.ks_2samp(df[df["source"] == "aa"]['direction'], df[df["source"] == "aa12"]['direction']).pvalue)
    total.append(
        stats.ks_2samp(df[df["source"] == "aa"]['direction'], df[df["source"] == "aa1"]['direction']).pvalue)
    total.append(
        stats.ks_2samp(df[df["source"] == "aa"]['direction'], df[df["source"] == "aa2"]['direction']).pvalue)

    total.append(stats.ks_2samp(df[df["source"] == "aa012"]['direction'],
                                df[df["source"] == "aa"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa012"]['direction'],
                                df[df["source"] == "aa01"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa012"]['direction'],
                                df[df["source"] == "aa02"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa012"]['direction'],
                                df[df["source"] == "aa0"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa012"]['direction'],
                                df[df["source"] == "aa12"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa012"]['direction'],
                                df[df["source"] == "aa1"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa012"]['direction'],
                                df[df["source"] == "aa2"]['direction']).pvalue)

    total.append(
        stats.ks_2samp(df[df["source"] == "aa01"]['direction'], df[df["source"] == "aa"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa01"]['direction'],
                                df[df["source"] == "aa012"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa01"]['direction'],
                                df[df["source"] == "aa02"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa01"]['direction'],
                                df[df["source"] == "aa0"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa01"]['direction'],
                                df[df["source"] == "aa12"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa01"]['direction'],
                                df[df["source"] == "aa1"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa01"]['direction'],
                                df[df["source"] == "aa2"]['direction']).pvalue)

    total.append(
        stats.ks_2samp(df[df["source"] == "aa02"]['direction'], df[df["source"] == "aa"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa02"]['direction'],
                                df[df["source"] == "aa012"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa02"]['direction'],
                                df[df["source"] == "aa01"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa02"]['direction'],
                                df[df["source"] == "aa0"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa02"]['direction'],
                                df[df["source"] == "aa12"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa02"]['direction'],
                                df[df["source"] == "aa1"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa02"]['direction'],
                                df[df["source"] == "aa2"]['direction']).pvalue)

    total.append(
        stats.ks_2samp(df[df["source"] == "aa0"]['direction'], df[df["source"] == "aa"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa0"]['direction'],
                                df[df["source"] == "aa012"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa0"]['direction'],
                                df[df["source"] == "aa01"]['direction']).pvalue)
    total.append(
        stats.ks_2samp(df[df["source"] == "aa0"]['direction'], df[df["source"] == "aa2"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa0"]['direction'],
                                df[df["source"] == "aa12"]['direction']).pvalue)
    total.append(
        stats.ks_2samp(df[df["source"] == "aa0"]['direction'], df[df["source"] == "aa1"]['direction']).pvalue)
    total.append(
        stats.ks_2samp(df[df["source"] == "aa0"]['direction'], df[df["source"] == "aa2"]['direction']).pvalue)

    total.append(
        stats.ks_2samp(df[df["source"] == "aa12"]['direction'], df[df["source"] == "aa"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa12"]['direction'],
                                df[df["source"] == "aa012"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa12"]['direction'],
                                df[df["source"] == "aa01"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa12"]['direction'],
                                df[df["source"] == "aa2"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa12"]['direction'],
                                df[df["source"] == "aa0"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa12"]['direction'],
                                df[df["source"] == "aa1"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa12"]['direction'],
                                df[df["source"] == "aa2"]['direction']).pvalue)

    total.append(
        stats.ks_2samp(df[df["source"] == "aa1"]['direction'], df[df["source"] == "aa"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa1"]['direction'],
                                df[df["source"] == "aa012"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa1"]['direction'],
                                df[df["source"] == "aa01"]['direction']).pvalue)
    total.append(
        stats.ks_2samp(df[df["source"] == "aa1"]['direction'], df[df["source"] == "aa2"]['direction']).pvalue)
    total.append(
        stats.ks_2samp(df[df["source"] == "aa1"]['direction'], df[df["source"] == "aa0"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa1"]['direction'],
                                df[df["source"] == "aa12"]['direction']).pvalue)
    total.append(
        stats.ks_2samp(df[df["source"] == "aa1"]['direction'], df[df["source"] == "aa2"]['direction']).pvalue)

    total.append(
        stats.ks_2samp(df[df["source"] == "aa2"]['direction'], df[df["source"] == "aa"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa2"]['direction'],
                                df[df["source"] == "aa012"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa2"]['direction'],
                                df[df["source"] == "aa01"]['direction']).pvalue)
    total.append(
        stats.ks_2samp(df[df["source"] == "aa2"]['direction'], df[df["source"] == "aa2"]['direction']).pvalue)
    total.append(
        stats.ks_2samp(df[df["source"] == "aa2"]['direction'], df[df["source"] == "aa0"]['direction']).pvalue)
    total.append(stats.ks_2samp(df[df["source"] == "aa2"]['direction'],
                                df[df["source"] == "aa12"]['direction']).pvalue)
    total.append(
        stats.ks_2samp(df[df["source"] == "aa2"]['direction'], df[df["source"] == "aa1"]['direction']).pvalue)

    logger.info(total)
    logger.info(np.mean(np.array(total)))
    logger.info(np.std(np.array(total)))



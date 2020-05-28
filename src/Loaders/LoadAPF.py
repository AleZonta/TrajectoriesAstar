"""
GTEA. Turing Learning system to generate trajectories
Copyright (C) 2018  Alessandro Zonta (a.zonta@vu.nl)

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
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import tqdm as tqdm


class LoadAPF(object):
    """
    Loads the APF from file
    """
    def __init__(self, path, logger=None):
        self._path = path
        self._log = logger
        self.apf = None
        self.coordinates = {}
        self.x_values = []
        self.y_values = []

    def load_apf_only_routing_system(self):
        """
         Loads the APF from file
        :return:
        """
        if self._log is not None:
            self._log.debug("Loading APF from file...")
        self.apf = pd.read_csv(self._path, dtype='int8')
        # self.apf.info(verbose=False)
        if self._log is not None:
            self._log.info("APF with routing system loaded {}".format(self.apf.shape))

    def save_apf(self, path_file="apf.csv"):
        """
        Saves the APF to file
        :param path_file: path of the file to save
        :return:
        """
        if self.apf is not None:
            if self._log is not None:
                self._log.debug("Saving the APF on file...")
            self.apf.to_csv(path_file)
            if self._log is not None:
                self._log.info("APF saved on file/")

    def show_heatmap(self):
        """
        Prints heat map of the APF
        :return:
        """
        if self.apf is not None:
            if self._log is not None:
                self._log.debug("Displaying heat map...")
            plt.pcolor(self.apf)
            plt.axis('off')
            plt.colorbar()

            plt.show()

    def print_heatmap(self, save_name="heatmap.png"):
        """
        Prints heat map of the APF and save it to file
        :param save_name: name of the file to save
        :return:
        """
        if self.apf is not None:
            if self._log is not None:
                self._log.debug("Saving heat map...")

            plt.pcolor(self.apf)
            plt.axis('off')
            plt.colorbar()
            plt.clim(0, 100)

            plt.savefig(save_name, dpi=50, facecolor='w', edgecolor='w', orientation='portrait',
                        papertype=None,
                        format=None, transparent=False, bbox_inches=None, pad_inches=0.1,
                        frameon=None, )
            plt.close()
            if self._log is not None:
                self._log.info("Heat map saved.")

    def invert_apf(self):
        """
        Invert the APF
        :return:
        """
        if self.apf is not None:
            if self._log is not None:
                self._log.debug("Inverting Heat Map.")
            self.apf = self.apf.iloc[::-1]

    def match_index_with_coordinates(self):
        """
        The APF has index from 0 to N
        Every cells correspond to real world coordinates
        This method matches the to systems
        :return:
        """
        if self._log is not None:
            self._log.info("Loading real coordinate and creating matching for the indexes.")
        # loading coordinates
        self.coordinates = LoadConfigs.configurations["coordinates"]

        # resolution image
        x_max = self.apf.shape[0]
        y_max = self.apf.shape[1]

        # creation of the real coordinates
        # now the index correspond to a real coordinate
        self.x_values = np.linspace(start=self.coordinates["west"], stop=self.coordinates["east"], num=x_max)
        self.y_values = np.linspace(start=self.coordinates["south"], stop=self.coordinates["north"], num=y_max)

    def check_if_something_is_there(self):
        """
        Chesk if the APF has data on it
        :return:
        """
        if self.apf is not None:
            x_max = self.apf.shape[0]
            y_max = self.apf.shape[1]
            count = 0

            all_the_indexes = []
            for x in range(0, x_max):
                for y in range(0, y_max):
                    all_the_indexes.append((x, y))

            for i in tqdm.tqdm(range(len(all_the_indexes))):
                x = all_the_indexes[i][0]
                y = all_the_indexes[i][1]
                if self.apf.loc[x][y] != 0:
                    print("{}, {}, {}".format(x,y,self.apf.loc[x][y]))
                    count += 1

            self._log.debug("No zeros elements {}".format(count))
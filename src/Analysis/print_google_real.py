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
import json
import logging
import os

import folium
import numpy as np

class PrintReal(object):
    def __init__(self, log):
        self._log = log
        self._tra = None

    def read_data(self, path):
        """
        Read real trajectories
        :param path: path where to find the real trajectories
        :return:
        """
        with open(path, 'r') as f:
            self._tra = json.load(f)

    def print_tra(self, path_to_save):
        """
        Print real trajectories over a OSM overlay
        :param path_to_save: where to save the trajectories
        :return:
        """
        if self._tra is None:
            raise FileNotFoundError("Load trajectories first")

        path_here = "{}/google_pics/".format(path_to_save)
        os.makedirs(path_here, exist_ok=True)

        for i in range(self._tra["size"]):
            name_tra = "Trajectory-" + str(i)
            tra_selected = self._tra[name_tra]
            x = []
            y = []
            coordinates = []
            for points in tra_selected:
                x.append(float(points[0]))
                y.append(float(points[1]))
                coordinates.append([float(points[0]), float(points[1])])
            x = x[:500]
            y = y[:500]
            coordinates = coordinates[:500]

            m = folium.Map(location=[np.mean(np.array(x)), np.mean(np.array(y))], zoom_start=13)

            my_PolyLine = folium.PolyLine(locations=coordinates, weight=5)
            m.add_children(my_PolyLine)
            m.save("{}/real_map_{}.html".format(path_here, i))


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

    a = PrintReal(log=logger)
    a.read_data(path="/Users/alessandrozonta/PycharmProjects/GTEA/Data/small_sport.json")
    a.print_tra(path_to_save="/Users/alessandrozonta/Desktop/data/real_tra")
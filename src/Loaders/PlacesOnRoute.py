"""
TLSTM. Turing Learning system to generate trajectories
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
import math

import glob
import logging
import multiprocessing
import numpy as np
import pandas as pd
import random
import tqdm
from sklearn.externals.joblib import Parallel, delayed
from tqdm import trange

from src.Utils.Point import Point






def find_route(apf, points, values_already_visited):
    """
    Check if the points passed are on the road or not
    :param apf: Dataframe describing the routing system
    :param points: points to check if they are on a road
    :param values_already_visited: list of points already visited by the search
    :return: return the Point if it is on the road, otherwise returns None
    """
    for point in points:
        if not is_in_list(list_of_points=values_already_visited, point_to_check=point):
            if apf.iloc[point.x][point.y] != 0:
                return point
            else:
                values_already_visited.append(point)
    return None


def check_if_inside_bounds(apf, points):
    """
    Method that checks if points are inside the boundaries of the map
    :param apf: matrix describing the area
    :param points: points to check
    :return: points inside boundaries
    """
    x_bound = apf.shape[0]
    y_bound = apf.shape[1]
    points_inside_boudaries = []
    for p in points:
        if 0 < p.x < x_bound and 0 < p.y < y_bound:
            points_inside_boudaries.append(p)
    return points_inside_boudaries


def find_nearest(array, value):
    """
    Find nearest value in the array provided.

    example:
    array = [0,1,2,3,4,5,6,7]
    value = [2.2]

    result = 2

    :param array: array where to find the closest value
    :param value: original value
    :return: closest value
    """
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]


def find_closest_in_road(apf, starting_point, values_matrix):
    """
    Find closest point to the given one that is over a road
    :param apf: dataframe describing the road system
    :param starting_point: original point
    :param values_matrix: matching index matrix with real world coordinates
    :return: point closest to the original one but over a road
    """
    x_point = starting_point[0]
    y_point = starting_point[1]

    x_values = values_matrix[0]
    y_values = values_matrix[1]

    matrix_x = np.where(x_values == x_point)[0][0]
    matrix_y = np.where(y_values == y_point)[0][0]

    values_already_visited = [Point(x=matrix_x, y=matrix_y)]

    points = list_neighbours(x_value=matrix_x, y_value=matrix_y, list_already_visited=values_already_visited)
    points = check_if_inside_bounds(apf=apf, points=points)

    point_found = find_route(apf=apf, points=points, values_already_visited=values_already_visited)

    if point_found is not None:
        return point_found

    while point_found is None:
        remember_points_locally = []
        for i in trange(len(points)):
            point = points[i]
            points_locally = list_neighbours(x_value=point.x, y_value=point.y,
                                             list_already_visited=values_already_visited)
            point_found = find_route(apf=apf, points=points_locally, values_already_visited=values_already_visited)

            if point_found is not None:
                break
            for p in points_locally:
                remember_points_locally.append(p)

        if point_found is not None:
            return point_found

        # points = []
        # for p in remember_points_locally:
        #     points.append(p)
        points = [p for p in remember_points_locally]


def random_wrapper_uniform(lower_bound, upper_bound):
    return random.uniform(lower_bound, upper_bound)


def random_wrapper_randint(lower_bound, upper_bound):
    return random.randint(lower_bound, upper_bound)


def worker(index, section, boundaries, values_matrix, apf):
    # print("starting {} worker".format(index))
    start = int(section[0])
    end = int(section[1])
    for i in range(start, end):
        point_found = {}

        # generate random point between boundaries
        x_coordinate = random_wrapper_uniform(lower_bound=boundaries["west"],
                                              upper_bound=boundaries["east"])
        y_coordinate = random_wrapper_uniform(lower_bound=boundaries["south"],
                                              upper_bound=boundaries["north"])

        # match coordinates with what it is represented by the matrix
        real_x = find_nearest(array=values_matrix[0], value=x_coordinate)
        real_y = find_nearest(array=values_matrix[1], value=y_coordinate)

        matrix_x = np.where(values_matrix[0] == real_x)[0][0]
        matrix_y = np.where(values_matrix[1] == real_y)[0][0]

        # check if it is a road or not
        if apf.iloc[matrix_x][matrix_y] == 0:
            # not in a road, need to find closest point in a road
            real_point_on_the_road = find_closest_in_road(apf=apf, starting_point=(real_x, real_y),
                                                          values_matrix=values_matrix)
            matrix_x = real_point_on_the_road.x
            matrix_y = real_point_on_the_road.y

        point_found.update({i: (matrix_x, matrix_y)})

        dfs = pd.DataFrame(point_found)

        dfs.to_csv("preload_positions_small_matrix_" + str(index) + ".csv")


def worker(index, boundaries, values_matrix, apf):
    # print("starting {} worker".format(index))
    point_found = {}

    # generate random point between boundaries
    x_coordinate = random_wrapper_uniform(lower_bound=boundaries["west"],
                                          upper_bound=boundaries["east"])
    y_coordinate = random_wrapper_uniform(lower_bound=boundaries["south"],
                                          upper_bound=boundaries["north"])

    # match coordinates with what it is represented by the matrix
    real_x = find_nearest(array=values_matrix[0], value=x_coordinate)
    real_y = find_nearest(array=values_matrix[1], value=y_coordinate)

    matrix_x = np.where(values_matrix[0] == real_x)[0][0]
    matrix_y = np.where(values_matrix[1] == real_y)[0][0]

    # check if it is a road or not
    if apf.iloc[matrix_x][matrix_y] == 0:
        # not in a road, need to find closest point in a road
        real_point_on_the_road = find_closest_in_road(apf=apf, starting_point=(real_x, real_y),
                                                      values_matrix=values_matrix)
        matrix_x = real_point_on_the_road.x
        matrix_y = real_point_on_the_road.y

    point_found.update({index: (matrix_x, matrix_y)})

    dfs = pd.DataFrame(point_found)

    dfs.to_csv("/Volumes/Cthulhu/GTEA/preload_inner_points/preload_positions_small_matrix_" + str(index) + ".csv")


class FindPlacesOnRoutes(object):
    """
    Find random places among the route system loaded in the APF.
    The previous files are only copy of the other classes present in the projects.
    This was necessary in order to have only one file running in different computer in order to make the process faster
    Did not have time to copy the entire project

    I know this is something not to do

    But for this time is okay, if comment are not present in the classes above this one, go in the project and find the
    file where that method is implemented and hopefully you will find useful comment there
    """

    def __init__(self, logger, apf=None, boundaries=None, values_matrix=None):
        self.log = logger
        self.apf = apf
        self.boundaries = boundaries
        self.values_matrix = values_matrix
        self.values = None

    def preload_positions(self, how_many):
        """
        Since loading the position during the run is too time consuming, this method does that before it and
        stores the points in a dataframe and in a csv file
        :param how_many: how many points I am looking for
        :return:
        """
        number_of_processes = multiprocessing.cpu_count() - 1
        with Parallel(n_jobs=number_of_processes, verbose=30) as parallel:
            parallel(delayed(worker)(i, self.boundaries, self.values_matrix, self.apf)
                     for i in range(how_many))

    def load_preloaded_position(self):
        """
        The meaning of this method is too easy to write down a useful comment.
        Instead I am loosing time writing these meaningless lines only for you that are going to read them.
        But be realistic.
        No one will ever read this comments.
        PhD hard life
        :return:
        """
        self.log.debug("Loading point already found in advance...")
        # root = os.path.dirname(os.path.abspath(__file__))
        # positions_file = root.replace("PreComputations", "") + "/Data/preload_positions_small_area_with_limits_total.csv"
        starting_point_train = np.load(
            "/Users/alessandrozonta/PycharmProjects/deapGeneration/Data/real_tra_test_starting_points.npy",
            allow_pickle=True)

        # self.values = pd.read_csv(positions_file)
        self.values = starting_point_train
        # self.values.info(verbose=False)
        # self.values = self.values.astype('int8')
        # self.values.info(verbose=False)
        self.log = None

    def get_point(self, idx_tra):
        first_point_str = self.values[idx_tra].split("-")
        starting_position_x = int(first_point_str[0])
        starting_position_y = int(first_point_str[1])
        return starting_position_x, starting_position_y

    def get_random_point(self):
        """
        Draw a random number from 0 to how many points are present in the dataset and return the coordinates x and y
        of that point
        :return:
        """
        idx = random_wrapper_randint(0, self.values.shape[0] - 1)
        line = self.values.iloc[idx]
        return line[1], line[2], line[3], line[4]

    def transpose_and_save(self):
        self.values = self.values.transpose()
        self.values.to_csv("transposed_preload_positions.csv")

    def load_all_preload_files(self, location):
        """
        load all the different csv with the positions and make only one
        :return:
        """
        files_to_find = location + "/preload_positions_small_matrix*"
        all_the_csv = glob.glob(files_to_find)

        x = []
        y = []
        for csv in all_the_csv:
            value = pd.read_csv(csv)
            coordinates = value.iloc[:, 1].tolist()
            x.append(coordinates[0])
            y.append(coordinates[1])

        total = {"x": x, "y": y}
        df = pd.DataFrame(data=total)
        df.to_csv("preload_positions_small_area_small_matrix.csv")

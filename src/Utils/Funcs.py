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
from src.Utils.Point import Point


def list_neighbours(x_value, y_value, apf, list_already_visited=None):
    """
    Return all the neighbours cells.
    If the neighbour is already visited, it is removed from the return list
    :param x_value: x value starting point
    :param y_value: y value starting point
    :param list_already_visited: list of point already visited
    :return: list of neighbours
    """
    xx = [x_value - 1, x_value, x_value + 1, x_value + 1, x_value + 1, x_value, x_value - 1, x_value - 1]
    yy = [y_value + 1, y_value + 1, y_value + 1, y_value, y_value - 1, y_value - 1, y_value - 1, y_value]

    # remove negative values and values outside bounds apf
    to_erase_x = []
    for i in range(len(xx) - 1, -1, -1):
        if xx[i] < 0:
            to_erase_x.append(i)
        if xx[i] >= apf[0]:
            to_erase_x.append(i)
    to_erase_y = []
    for i in range(len(yy) - 1, -1, -1):
        if yy[i] < 0:
            to_erase_y.append(i)
        if yy[i] >= apf[1]:
            to_erase_x.append(i)

    for i in range(len(xx) - 1, -1, -1):
        erase = False
        if i in to_erase_x or i in to_erase_y:
            erase = True
        if erase:
            del xx[i]
            del yy[i]

    points = []
    for i in range(len(xx)):
        p = Point(xx[i], yy[i])
        if not is_in_list(list_of_points=list_already_visited, point_to_check=p):
            points.append(p)
    return points


def is_in_list(list_of_points, point_to_check):
    """
    Check if a point is already in the list.
    If the list of points is empty or not used, the functions returns False

    :param list_of_points: list of points where to check
    :param point_to_check: point to check
    :return: Boolean Value: True if it is in the list, False otherwise
    """
    if list_of_points is None:
        return False
    for el in list_of_points:
        if el.equals(p1=point_to_check):
            return True
    return False

def compute_charge_points(genome, genome_meaning, current_position, K, pre_matrix):
    """
    Compute the attraction of the points
    :param genome: genome
    :param genome_meaning: meaning if every pos of the genome
    :param values_matrix: values to translate cells to coordinates
    :param current_position: current position
    :param K: constant for the computation of the charge
    :param pre_matrix: pre computation of distance from the cell to the objects
    :return: total charge
    """
    # now prematrix is the cell system optimised
    # start_time = time.time()
    total_charge = pre_matrix.return_charge_from_point(current_position=current_position, genome=genome,
                                                       genome_meaning=genome_meaning, K=K)

    # current_time = time.time()
    # time_from_start = current_time - start_time  # time in seconds
    # print(time_from_start)
    return total_charge

def keep_only_points_on_street(apf, points):
    """
    Check if the points provided are on a route
    :param apf: Dataframe describing the routing system
    :param points: list of points to check
    :return: list of points from the input list that are actually on a route
    """
    points_on_street = []
    for p in points:
        # print("{}-{} -> {}".format(int(p.x), int(p.y), apf.iloc[int(p.x)][int(p.y)]))
        if apf.iloc[int(p.x)][int(p.y)] != 0:
            points_on_street.append(p)
    return points_on_street


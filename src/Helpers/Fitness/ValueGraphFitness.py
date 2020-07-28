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
import pickle

from scipy.spatial import distance
from shapely.geometry import Point

from src.Settings.args import args

VAL_NO_DATA = -1
LIMIT_TIMESTEPS = 5000
MAX_FITNESS = 200
MAX_TOTAL_FITNESS = MAX_FITNESS * 3


def _get_fitness_length_curliness(point, external, internal):
    """
    Get fitness value
    :param point: current features
    :param external: external hull fitness function
    :param internal: internal hull fitness function
    :return: distance
    """
    if internal.contains(point):
        actual_distance = 0
    elif external.contains(point):
        actual_distance = point.distance(internal)
    else:
        actual_distance = -point.distance(external)
    # if actual_distance < -150:
    #     actual_distance = -150
    return actual_distance


def _get_distance_to_center(point, internal, new_min=-300):
    """
    Return distance to center of the hull
    :param point: current features
    :param internal: polygon
    :param new_min: min value to normalise the distance to
    :return: fitness value normalised and raw
    """
    centroid = internal.centroid
    d = -distance.euclidean([centroid.x, centroid.y], [point.x, point.y])
    max_value = -5000
    if d < max_value:
        d = max_value
    fitness_value = convert(old_max=0, old_min=max_value, new_max=MAX_FITNESS, new_min=new_min, old_value=d)
    return fitness_value, d


def _get_combination_two_fitness_curliness_length(point, internal_normal, internal_special, external):
    """
    return fitness from two features (curliness and length).
    Depending on the result, it returns the value from the center or the normalised value
    :param point: current features
    :param internal_normal: internal hull of the fitness landascape
    :param internal_special: internal hull of the fitness landascape
    :param external: external hull of the fitness landscape
    :return:  fitness value current combination of fitness
    """
    value_from_curliness_length = _get_fitness_length_curliness(point=point,
                                                                external=external,
                                                                internal=internal_normal)
    if value_from_curliness_length == 0:
        value_from_curliness_length, _ = _get_distance_to_center(point=point,
                                                                 internal=internal_special, new_min=100)
    else:
        value_from_curliness_length = convert(old_max=0, old_min=-150, new_max=100, new_min=-300,
                                              old_value=value_from_curliness_length)
    return value_from_curliness_length


def _get_combination_two_fitness_curliness_distance(point, internal_normal, internal_special, external):
    """
        return fitness from two features (curliness and distance).
        Depending on the result, it returns the value from the center or the normalised value
        :param point: current features
        :param internal_normal: internal hull of the fitness landascape
        :param internal_special: internal hull of the fitness landascape
        :param external: external hull of the fitness landscape
        :return:  fitness value current combination of fitness
        """
    value_from_curliness_distance = _get_fitness_length_curliness(point=point,
                                                                  external=external,
                                                                  internal=internal_normal)
    if value_from_curliness_distance == 0:
        value_from_curliness_distance, _ = _get_distance_to_center(point=point,
                                                                   internal=internal_special, new_min=100)
    else:
        value_from_curliness_distance = convert(old_max=0, old_min=-150, new_max=100, new_min=-300,
                                                old_value=value_from_curliness_distance)
    return value_from_curliness_distance


def _get_combination_two_fitness_length_distance(point, internal_normal, internal_special, external):
    """
        return fitness from two features (distance and length).
        Depending on the result, it returns the value from the center or the normalised value
        :param point: current features
        :param internal_normal: internal hull of the fitness landascape
        :param internal_special: internal hull of the fitness landascape
        :param external: external hull of the fitness landscape
        :return:  fitness value current combination of fitness
        """
    value_from_distance_length = _get_fitness_length_curliness(point=point, external=external,
                                                               internal=internal_normal)
    if value_from_distance_length == 0:
        value_from_distance_length, _ = _get_distance_to_center(point=point, internal=internal_special,
                                                                new_min=100)
    else:
        value_from_distance_length = convert(old_max=0, old_min=-150, new_max=100, new_min=-300,
                                             old_value=value_from_distance_length)
    return value_from_distance_length


def get_fitness_value(length, curliness, further_distance):
    """
    Return the fitness value based on the features
    :param length: length of the current path
    :param curliness: curliness of the path
    :param further_distance: further distance to start of the current path
    :return: fitness value
    """
    fitness_landscape = pickle.load(open("{}/3d_fitness_in_2d_with_limitation.pickle".format(args.data_path), 'rb'))
    point_distance = args.point_distance
    if point_distance is None:
        point_distance = []

    point = Point(curliness * 100, length)

    if 0 in point_distance:
        value_from_curliness_length = \
            _get_combination_two_fitness_curliness_length(point=point, internal_normal=fitness_landscape[1],
                                                          external=fitness_landscape[0],
                                                          internal_special=fitness_landscape[6])
        # value_from_curliness_length, _ = _get_distance_to_center(point=point, internal=fitness_landscape[6])
    else:
        value_from_curliness_length = _get_fitness_length_curliness(point=point, external=fitness_landscape[0],
                                                                    internal=fitness_landscape[1])
        value_from_curliness_length = convert(old_max=0, old_min=-150, new_max=MAX_FITNESS, new_min=-300,
                                              old_value=value_from_curliness_length)

    point = Point(curliness * 100, further_distance)
    if 1 in point_distance:
        value_from_curliness_distance = \
            _get_combination_two_fitness_curliness_distance(point=point, internal_normal=fitness_landscape[3],
                                                            external=fitness_landscape[2],
                                                            internal_special=fitness_landscape[8])
        # value_from_curliness_distance, _ = _get_distance_to_center(point=point, internal=fitness_landscape[8])
    else:
        value_from_curliness_distance = _get_fitness_length_curliness(point=point, external=fitness_landscape[2],
                                                                      internal=fitness_landscape[3])
        value_from_curliness_distance = convert(old_max=0, old_min=-150, new_max=MAX_FITNESS, new_min=-300,
                                              old_value=value_from_curliness_distance)

    point = Point(further_distance, length)
    if 2 in point_distance:
        value_from_distance_length = \
            _get_combination_two_fitness_length_distance(point=point, internal_normal=fitness_landscape[5],
                                                         external=fitness_landscape[4],
                                                         internal_special=fitness_landscape[10])
        # value_from_distance_length, _ = _get_distance_to_center(point=point, internal=fitness_landscape[10])
    else:
        value_from_distance_length = _get_fitness_length_curliness(point=point, external=fitness_landscape[4],
                                                                   internal=fitness_landscape[5])
        value_from_distance_length = convert(old_max=0, old_min=-150, new_max=MAX_FITNESS, new_min=-300,
                                              old_value=value_from_distance_length)

    return value_from_distance_length + value_from_curliness_length + value_from_curliness_distance, \
           value_from_distance_length, value_from_curliness_length, value_from_curliness_distance


def convert(old_max, old_min, new_max, new_min, old_value):
    """
    Convert one value to another scale
    :param old_max: old max
    :param old_min: old min
    :param new_max: new max
    :param new_min: new min
    :param old_value: value to convert
    :return:
    """
    old_range = (old_max - old_min)
    new_range = (new_max - new_min)
    new_value = (((old_value - old_min) * new_range) / old_range) + new_min
    return new_value


def get_next_point(current_point, direction):
    """
    Based on the current coordinate and the direction return the next point
    :param current_point: current location
    :param direction: direction to move
    :return: next direction
    """
    x_value = current_point.x
    y_value = current_point.y
    if direction == 0:
        return x_value - 1, y_value + 1
    elif direction == 1:
        return x_value, y_value + 1
    elif direction == 2:
        return x_value + 1, y_value + 1
    elif direction == 3:
        return x_value + 1, y_value
    elif direction == 4:
        return x_value + 1, y_value - 1
    elif direction == 5:
        return x_value, y_value - 1
    elif direction == 6:
        return x_value - 1, y_value - 1
    elif direction == 7:
        return x_value - 1, y_value
    else:
        raise Exception()


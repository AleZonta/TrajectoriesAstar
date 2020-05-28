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

from haversine import haversine

from src.Utils.Funcs import list_neighbours, keep_only_points_on_street, compute_charge_points


def chain_of_neighbours(total_distance, genome, genome_meaning, values_matrix, K, distances,
                        current_node, apf, pre_matrix):
    """
    From current position check the neighbours for the most attractive one and move there.
    Loop till reach maximum length

    -> check neighbours nodes in order to find the one with the strongest attraction
    -> check only neighbours that have charge != 0 (in order to stay on routes)
    -> compute attraction points using coulomb law: |E| = k(|q|/r^2). r is computed using haversine measure
    -> move to the location with strongest attraction
    -> save the point as next point of the path
    -> increase counter of distance travelled
    -> repeat until I reach distance expressed by gene of genome

    :param total_distance:  total distance to travel
    :param genome: genome
    :param genome_meaning: meaning if every pos of the genome
    :param values_matrix: values to translate cells to coordinates
    :param K: constant for the computation of the charge
    :param distances: vector with distances positions
    :param current_node: current node
    :param apf: apf
    :param pre_matrix: pre computation of distance from the cell to the objects
    :return: path
    """
    path = []
    distance_travelled = 0
    while distance_travelled < total_distance:
        # return neighbours of current node
        points = list_neighbours(x_value=current_node.x, y_value=current_node.y, apf=apf)
        points_on_the_street = keep_only_points_on_street(apf=apf, points=points)

        if len(points_on_the_street) == 0:
            # I cannot move in a street around me
            path.append(current_node)
            break

        # compute charge close points
        charges = [compute_charge_points(genome=genome,
                                         genome_meaning=genome_meaning,
                                         current_position=current_position, K=K, pre_matrix=pre_matrix) for
                   current_position in points_on_the_street]

        # find most attractive point
        most_attractive_point = points_on_the_street[charges.index(max(charges))]

        # adding point to path
        path.append(most_attractive_point)
        # compute distance

        dis = haversine((values_matrix[0][current_node.x], values_matrix[1][current_node.y]),
                        (values_matrix[0][most_attractive_point.x],
                         values_matrix[1][most_attractive_point.y])) * 1000  # in metres
        distances.append(dis)
        distance_travelled += dis

        current_node = most_attractive_point
    return path

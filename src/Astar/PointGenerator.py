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
from src.Astar.Astar import astar
from src.Astar.Neighbours import chain_of_neighbours


class PointGenerator(object):
    """
    Proxy class for the method used to generate the path
    """
    def __init__(self, typology_needed, pre_matrix, type_astar):
        if typology_needed == "astar":
            self._type = 1
        elif typology_needed == "default":
            self._type = 0
        else:
            raise ValueError("Type requested not implemented")
        self.type_astar = type_astar
        self.pre_matrix = pre_matrix

    def get_path(self, total_distance, genome, genome_meaning, values_matrix, K, distances,
                 current_node, apf, x_value):
        """
        Return the path with the method chosen to use
        :param total_distance:  total distance to travel
        :param genome: genome
        :param genome_meaning: meaning if every pos of the genome
        :param values_matrix: values to translate cells to coordinates
        :param K: constant for the computation of the charge
        :param distances: vector with distances positions
        :param current_node: current node
        :param apf: apf
        :return: path generated
        """
        if self._type == 0:
            return chain_of_neighbours(total_distance=total_distance,
                                       genome=genome, genome_meaning=genome_meaning, values_matrix=values_matrix, K=K,
                                       distances=distances, current_node=current_node, apf=apf,
                                       pre_matrix=self.pre_matrix)
        else:
            return astar(apf=apf, start=current_node, distance_target=total_distance,
                         genome=genome,
                         values_matrix=values_matrix, K=K, pre_matrix=self.pre_matrix, x_value=x_value,
                         type_astar=self.type_astar)

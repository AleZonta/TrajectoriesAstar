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
import heapq

from haversine import haversine

from src.Utils.Funcs import list_neighbours, compute_charge_points


class Node(object):
    """A node class for A* Pathfinding"""

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0  # distance from start
        self.h = 0  # estimate distance from end
        self.f = 0  # total cost cell
        self.id = self.position.to_key()

    def __eq__(self, other):
        return self.position == other.position

    def __str__(self):
        return "{}, {}. g={}; h={}; f={}, parent={},{}".format(self.position.x, self.position.y, self.g, self.h, self.f,
                                                               self.parent.position.x if self.parent is not None else 0
                                                               , self.parent.position.y if
                                                               self.parent is not None else 0)

    def __lt__(self, other):
        return self.f < other.f


def astar(apf, start, distance_target, genome, genome_meaning, values_matrix, K, pre_matrix, x_value,
          type_astar):
    """
    Returns a list of tuples as a path from the given start to the given end in the given maze
    This is a normal a star algorithm is supposed to work

    The current version does not know the destination point
    It only knows the distance from the destination point

    :param apf: matrix representing the routing system of the area
    :param start: starting point
    :param distance_target: distance from the target (total length trip)
    :param genome: genome
    :param genome_meaning: meaning if every pos of the genome
    :param values_matrix: values to translate cells to coordinates
    :param K: constant for computing charge
    :param pre_matrix: pre computation of distance from the cell to the objects
    :param end_point: target node
    :param type_astar: typology of the astar wanted
    """
    # make x_value a percentege of the total distance target
    x_value = (distance_target * x_value) / 100

    # end_node = Node(parent=None, position=end_point)
    # if it takes too long, going to stop it
    # start_time = time.time()
    # Create start and end node
    start_node = Node(parent=None, position=start)
    start_node.g = start_node.h = start_node.f = 0

    # Initialize both open and closed list
    # open_list = []
    open_queue = []
    second_open_queue = {}
    closed_list = {}

    # Add the start node
    # open_list.append(start_node)
    heapq.heappush(open_queue, (start_node.f, start_node))
    second_open_queue.update({start_node.id: 0})

    # Loop until you find the end
    while len(open_queue) > 0:

        # Get the current node
        # current_node = open_list[0]
        # current_index = 0
        # for index, item in enumerate(open_list):
        #     if item.f < current_node.f:
        #         current_node = item
        #         current_index = index
        current_node = heapq.heappop(open_queue)[1]
        del second_open_queue[current_node.id]

        # with open("a_star_{}.txt".format(LoadConfigs.configurations["name_exp"]), "a") as myfile:
        #     myfile.write("current node -> {} \n".format(current_node))

        # Pop current off open list, add to closed list
        # open_list.pop(current_index)
        # closed_list.add(current_node)
        closed_list[current_node.id] = ""

        # current_time = time.time()
        # time_from_start = current_time - start_time  # time in seconds
        # block execution astar after 10 minutes -> hardcoded function

        # end = False
        # if time_from_start >= 300:
        #     end = True
        # find the bigger node.g
        # max_id = max(second_open_queue.items(), key=operator.itemgetter(1))[0]
        #
        # for el in open_queue:
        #     if el[1].id == max_id:
        #         current_node = el[1]
        #         break
        # distance_target = current_node.g - 10

        # Found the goal
        # on the cuxrrent node, the distance from the start is saved as g
        # so if the distance from the start is equals to distance_target then I found the goal
        # if current_node.id == end_node.id: # or end:
        if current_node.g >= distance_target:
            # with open("a_star_{}.txt".format(LoadConfigs.configurations["name_exp"]), "a") as myfile:
            #     myfile.write("closed list {}, open list {} \n".format(len(closed_list), len(second_open_queue)))
            #     myfile.write("------------------ \n")
            #     myfile.write("------------------ \n")
            #     myfile.write("------------------ \n")

            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            # print(open_queue)
            # print(closed_list)
            # print(path)
            return path[::-1]  # Return reversed path

        # Generate children
        points = list_neighbours(x_value=current_node.position.x, y_value=current_node.position.y, apf=apf)
        # points_on_the_street = keep_only_points_on_street(apf=pre_matrix.get_apf(), points=points)
        points_on_the_street = pre_matrix.keep_only_points_on_street(points=points)

        children = [Node(parent=current_node, position=node_position) for node_position in points_on_the_street]
        # for node_position in points_on_the_street:  # Adjacent squares
        #
        #     # Create new node
        #     new_node = Node(current_node, node_position)
        #
        #     # Append
        #     children.append(new_node)

        # Loop through children
        for child in children:
            # Child is on the closed list
            if closed_list.get(child.id, None) is not None:
                # if child in closed_list:
                continue

            # Child already computed
            if second_open_queue.get(child.id, None) is not None:
                # result = list(filter(lambda x: x[1] == child, open_queue))
                # if len(result) > 0:
                continue

            # Create the f, g, and h values
            r = haversine((values_matrix[0][child.position.x], values_matrix[1][child.position.y]),
                          (values_matrix[0][current_node.position.x],
                           values_matrix[1][current_node.position.y])) * 1000  # in metres
            child.g = current_node.g + r

            # distance to end is total distance - distance from start
            distance_to_end = distance_target - child.g
            # distance_to_end = haversine((values_matrix[0][child.position.x], values_matrix[1][child.position.y]),
            #                             (values_matrix[0][end_node.position.x],
            #                              values_matrix[1][end_node.position.y])) * 1000  # in metres

            child.h = abs(_compute_h(distance_to_end=distance_to_end, genome=genome,
                                     genome_meaning=genome_meaning, type_astar=type_astar,
                                     current_position=child.position, K=K, pre_matrix=pre_matrix, x_value=x_value))

            total_g_normalised = _standard_normalisation(old_value=child.g, old_min=0, old_max=distance_target + 100,
                                                         new_min=0, new_max=10)
            child.f = -(total_g_normalised + child.h)
            # child.f = -child.h

            # Child is already in the open list
            # result = list(filter(lambda x: x[1] == child, open_queue))
            # if len(result) > 0 and child.g > result[0].g:
            #     continue
            res = second_open_queue.get(child.id, None)
            # if res is not None:
            #     print("S")
            if res is not None and child.g > res:
                continue

            # print(child)
            # Add the child to the open list
            # open_list.append(child)
            heapq.heappush(open_queue, (child.f, child))
            second_open_queue.update({child.id: child.g})
            #
            # with open("a_star_{}.txt".format(LoadConfigs.configurations["name_exp"]), "a") as myfile:
            #     myfile.write("kid -> {} \n".format(child))


def _standard_normalisation(old_value, old_min, old_max, new_min, new_max):
    """
    Normalisation function
    :param old_value: old value to convert
    :param old_min: old minimum
    :param old_max: old maximum
    :param new_min: new minimum
    :param new_max: new maximum
    :return: value converted in the new range
    """
    return (((old_value - old_min) * (new_max - new_min)) / (old_max - old_min)) + new_min


def _compute_h(distance_to_end, genome, genome_meaning, current_position, K,
               pre_matrix, x_value, type_astar):
    """
    Custom way to compute the estimation for the distance to the target
    The idea is to have the heart distance to the target divided by the attraction of the cell

    More attractive the cell is, closer is going to be the distance

    The value is then multiplied by a constant 10
    :param distance_to_end: heart distance to the end
    :param genome: genome
    :param genome_meaning: meaning if every pos of the genome
    :param current_position: current position
    :param K: constant for the computation of the charge
    :param pre_matrix: pre computation of distance from the cell to the objects
    :param type_astar: typology of the astar wanted
    :return: value h needed from the A* algorithm
    """

    if type_astar == 0:
        total_charge = compute_charge_points(genome=genome,
                                             genome_meaning=genome_meaning,
                                             current_position=current_position, K=K, pre_matrix=pre_matrix)
        try:
            value = distance_to_end / (total_charge / total_charge - 0.005)
        except Exception as e:
            value = distance_to_end
    elif type_astar == 1:  # balanced attraction and distance
        total_charge = compute_charge_points(genome=genome,
                                             genome_meaning=genome_meaning,
                                             current_position=current_position, K=K, pre_matrix=pre_matrix)

        # need to balance the distance and the attractiveness
        # distance to end vs total_charge point.
        # value = 100 / (max(0, (x_value * 100) - distance_to_end) + total_charge)
        # value = max(0, (x_value * 100) - distance_to_end) + total_charge
        delta = (max(0, x_value - distance_to_end)) / (x_value + 0.000001)

        # need to normalise the values
        # for the total_charge we apply the Z-score: (value - mean) / std
        # mean and std have been computed in advance
        # but now I will use min max normaliser
        total_charge_normalised = _standard_normalisation(old_value=total_charge, old_min=0, old_max=10000, new_min=0,
                                                          new_max=10)
        distance_to_end_normalised = _standard_normalisation(old_value=distance_to_end, old_min=0, old_max=10000,
                                                             new_min=0, new_max=10)
        value = (1 - delta) * total_charge_normalised + delta * distance_to_end_normalised
        # value = total_charge_normalised
    elif type_astar == 2:  # only attraction
        total_charge = compute_charge_points(genome=genome,
                                             genome_meaning=genome_meaning,
                                             current_position=current_position, K=K, pre_matrix=pre_matrix)
        value = 100 / total_charge
    elif type_astar == 3:  # only distance to end
        value = distance_to_end
    else:
        raise Exception("astar typology not implemented")

    # value = x_value / (distance_to_end * total_charge)
    # value = distance_to_end - total_charge
    # print("value = distance_to_end / total_charge -> {} = {} / {}".format(value, distance_to_end, total_charge))
    return value

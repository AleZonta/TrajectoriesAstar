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
import sys

import glob
import os

import pandas as pd
import pickle
import seaborn as sns
import tqdm
from haversine import haversine
from shapely.geometry import Point
from tqdm import trange
from matplotlib import pyplot as plt

import numpy as np

from src.Division.CollectionCells import CollectionCells
from src.Division.HugeCells import HugeCell


class SubMatrix(object):
    def __init__(self, log, apf, list_points, values_matrix, save_and_store=True):
        self._log = log
        self._apf = apf
        self._list_points = list_points
        self._values_matrix = values_matrix
        self._list_of_cells = None
        self._match_key_index = None
        self._save_and_store = save_and_store
        self._division_point_x = None
        self._division_point_y = None
        self._real_coordinate_x = None
        self._real_coordinate_y = None
        self._has_been_updated = False

    def divide_into_cells(self, x_division, y_division, show=False, performance=True):
        """
        compute how many cells are required
        matches the id cell with real coordinates
        generate the right number of cell
        adds all the points to the correct cells
        print heatmap showing point per cell
        :param x_division: how many division in x axis
        :param y_division: how many division in y axis
        :param show: visualise the heatmap
        :return:
        """
        if self._log is not None:
            self._log.debug("Organising POIs into cells")

        x_values = self._apf.shape[0]
        y_values = self._apf.shape[1]

        every_how_many_x = int(x_values / x_division)
        every_how_many_y = int(y_values / y_division)

        self._division_point_x = np.arange(0, x_values, every_how_many_x).tolist()
        self._division_point_y = np.arange(0, y_values, every_how_many_y).tolist()
        if x_values - 1 not in self._division_point_x:
            self._division_point_x.append(x_values - 1)
        if y_values - 1 not in self._division_point_y:
            self._division_point_y.append(y_values - 1)

        self._real_coordinate_x = [self._values_matrix[0][x] for x in self._division_point_x]
        self._real_coordinate_y = [self._values_matrix[1][y] for y in self._division_point_y]
        self._real_coordinate_x[0] = self._real_coordinate_x[0] - 0.01
        self._real_coordinate_x[len(self._real_coordinate_x) - 1] = self._real_coordinate_x[
                                                                        len(self._real_coordinate_x) - 1] + 0.01
        self._real_coordinate_y[0] = self._real_coordinate_y[0] - 0.01
        self._real_coordinate_y[len(self._real_coordinate_y) - 1] = self._real_coordinate_y[
                                                                        len(self._real_coordinate_y) - 1] + 0.01

        self._match_key_index = {}
        keys = self._list_points.keys()
        count_here = 0
        for key in keys:
            self._match_key_index[key] = count_here
            count_here += 1
        number_of_features = len(keys)

        if self._log is not None:
            self._log.debug("Creation of the cells")
        self._list_of_cells = CollectionCells(matching=self._match_key_index, x_division=x_division,
                                              y_division=y_division, save_and_store=self._save_and_store)
        if performance:
            load = self._list_of_cells.load_stored_list_cells()
        else:
            load = self._list_of_cells.load_stored_list_cells(name="old_with_points_division_cell_list")
        if not load:
            for i in range(len(self._real_coordinate_x) - 1):
                for j in range(len(self._real_coordinate_y) - 1):
                    min_x = self._real_coordinate_x[i]
                    max_x = self._real_coordinate_x[i + 1] - 0.0000000001
                    min_y = self._real_coordinate_y[j]
                    max_y = self._real_coordinate_y[j + 1] - 0.0000000001
                    min_x_box = self._division_point_x[i]
                    max_x_box = self._division_point_x[i + 1]
                    min_y_box = self._division_point_y[j]
                    max_y_box = self._division_point_y[j + 1]

                    self._list_of_cells.add_cell(
                        HugeCell(min_x=min_x, min_y=min_y, max_x=max_x, max_y=max_y, position=(i, j),
                                 number_of_features=number_of_features, min_x_cell=min_x_box, min_y_cell=min_y_box,
                                 max_x_cell=max_x_box, max_y_cell=max_y_box))
            if self._log is not None:
                self._log.debug("division chosen {}x{} cells".format(x_division + 1, y_division + 1))
            self._list_of_cells.details_cell(self._log)

            if self._log is not None:
                self._log.debug("Point distributions")
            for key, value in self._list_points.items():
                if self._log is not None:
                    self._log.debug("__checking {}".format(key))
                for second_key, second_value in value.items():
                    for i in trange(len(second_value), desc="{} analysis".format(second_key)):
                        x = second_value[i][1]
                        y = second_value[i][0]
                        self._list_of_cells.assign_point(point=Point(x, y), index=self._match_key_index[key])
            if self._log is not None:
                self._log.debug(
                    "total number of point analysed {}. Points not assigned {}".format(self._list_of_cells.count_total,
                                                                                       self._list_of_cells.not_assigned))
            if self._log is not None:
                self._log.debug("indexing...")
            from tqdm import tqdm
            for c in tqdm(self._list_of_cells.get_all_cells(), desc="Indexing..."):
                c.define_indexing(apf=self._apf)

            # put into the correct cell
            if self._log is not None:
                self._log.debug("from precomputation to cells...")
            self.put_precomputed_into_cells(apf=self._apf)

            if self._log is not None:
                self._log.debug("creation points on road")
            for cell in self._list_of_cells.get_all_cells():
                cell.elaborate_points_on_road(apf=self._apf)

            if self._log is not None:
                self._log.debug("storing division to file")
            self._list_of_cells.store_current_list_cells()

        else:
            if self._log is not None:
                self._log.debug("Point division loaded from file")
            self._list_of_cells.load_mmap_data()

        if show:
            if self._log is not None:
                self._log.debug("Visualisation numbers")
            matrix = np.zeros((len(self._division_point_x), len(self._division_point_y)))
            for cell in self._list_of_cells.get_all_cells():
                pos = cell.position
                matrix[pos[0], pos[1]] = cell.return_number_elements()

            dataframe_apf = pd.DataFrame.from_records(matrix)
            # dataframe_apf = dataframe_apf.T
            ax = plt.axes()

            sns.heatmap(dataframe_apf, fmt="d", vmin=0, vmax=np.max(matrix), ax=ax)
            ax.set_title("Number of POIs per cell")
            plt.show()

        # for performance support
        self._log = None
        self._apf = None
        self._list_points = None
        if performance:
            self._division_point_x = None
            self._division_point_y = None
            self._values_matrix = None
            self._real_coordinate_x = None
            self._real_coordinate_y = None

    def return_charge_from_point(self, current_position, genome, genome_meaning, K):
        """
        return the charge from the current points using the cells system
        :param current_position: current position
        :param genome: genome evolved
        :param genome_meaning: meaning if every pos of the genome
        :param K: constant for the computation of the charge
        :return: double total charge
        """
        current_cell_id = self._list_of_cells.find_current_cell_from_matrix_coord(point=current_position)
        total_charge = 0
        cell = self._list_of_cells.get_cell_from_id(id=current_cell_id)

        index = 0
        for key, value in self._match_key_index.items():

            # get the charge
            charge = genome[genome_meaning.from_genome_to_value_describing_object(name_object=key)]

            # add to the total charge
            attractions_distances = cell.return_value_attraction(point=[current_position.x, current_position.y],
                                                                 index=index)
            if attractions_distances is None:
                raise ValueError()

            here_charge = K * charge * attractions_distances
            total_charge += here_charge

            index += 1

        return total_charge

    def return_charge_from_point_fallback(self, current_position, genome, genome_meaning, K, total_dict_data_new):
        """
        return the charge from the current points using the cells system if the precomputation part is not precomputed
        :param current_position: current position
        :param genome: genome evolved
        :param genome_meaning: meaning if every pos of the genome
        :param K: constant for the computation of the charge
        :return: double total charge
        """
        current_cell_id = self._list_of_cells.find_current_cell_from_matrix_coord(point=current_position)
        total_charge = 0
        cell = self._list_of_cells.get_cell_from_id(id=current_cell_id)

        index = 0

        precomputation = None
        for key, value in self._match_key_index.items():

            # get the charge
            charge = genome[genome_meaning.from_genome_to_value_describing_object(name_object=key)]

            # add to the total charge
            try:
                attractions_distances = cell.return_value_attraction(point=[current_position.x, current_position.y],
                                                                     index=index)
            except Exception as e:
                if total_dict_data_new.get("{}_{}".format(current_position.x, current_position.y)) is None:
                    # precompute and save in memory for future help
                    if precomputation is None:
                        precomputation = self.precompute_minimum_distance_and_equation(
                            current_position=current_position)
                    attractions_distances = precomputation["distances_per_tag"][index]["equation_precomputed_value"]
                else:
                    attractions_distances = \
                        total_dict_data_new["{}_{}".format(current_position.x, current_position.y)][
                            "distances_per_tag"][
                            index]["equation_precomputed_value"]

            here_charge = K * charge * attractions_distances
            total_charge += here_charge

            index += 1

        return total_charge, precomputation

    def return_distance_per_tag_precomputed(self, current_position):
        """
        Return list of precomputed distance for the equation from current position
        :param current_position: current position
        :return: list values
        """
        current_cell_id = self._list_of_cells.find_current_cell_from_matrix_coord(point=current_position)
        cell = self._list_of_cells.get_cell_from_id(id=current_cell_id)
        all_the_distances = []
        index = 0
        for _, _ in self._match_key_index.items():
            all_the_distances.append(cell.return_value_attraction(point=[current_position.x, current_position.y],
                                                                  index=index))
            index += 1
        return all_the_distances

    def return_min_distance_per_tag_precomputed(self, current_position):
        """
        Return list of precomputed distance for the equation from current position
        :param current_position: current position
        :return: list values
        """
        current_cell_id = self._list_of_cells.find_current_cell_from_matrix_coord(point=current_position)
        cell = self._list_of_cells.get_cell_from_id(id=current_cell_id)
        all_the_distances = []
        index = 0
        for _, _ in self._match_key_index.items():
            all_the_distances.append(cell.return_value_min_distance(point=[current_position.x, current_position.y],
                                                                    index=index))
            index += 1
        return all_the_distances

    def get_items(self):
        return list(self._match_key_index.items())

    def return_distance_from_point(self, current_position):
        """
        from the current position return the distance to the closest point
        Check the current cell. If there is not such a point, go to the nearest cells. TODO
        :param current_position: current position
        :return: vector of distances per tag
        """
        current_cell_id = self._list_of_cells.find_current_cell_from_matrix_coord(point=current_position)

        cell = self._list_of_cells.get_cell_from_id(id=current_cell_id)

        vector_distances = []
        for i in range(len(self._match_key_index.keys())):
            vector_distances.append(cell.return_value_min_distance(point=[current_position.x, current_position.y],
                                                                   index=i))
        return vector_distances

    def precompute_minimum_distance_and_equation(self, current_position):
        """
        Precompute the distance and the minimum distance from current position using the cell division idea
        :param current_position: position we are now
        :return: float minimum distance to object
        """
        current_cell_id = self._list_of_cells.find_current_cell_from_matrix_coord(point=current_position)

        neighbors_ids = self._list_of_cells.from_id_get_neighbours(current_id=current_cell_id)
        neighbors_ids.append(current_cell_id)

        all_the_distances = []
        for i in range(len(self._match_key_index.keys())):
            all_the_distances.append({"min_value_distace": sys.float_info.max, "equation_precomputed_value": 0})

        for cell in self._list_of_cells.get_all_cells():
            if cell.id in neighbors_ids:
                index_vector = 0
                for key, value in self._match_key_index.items():
                    # get position all the points
                    vector_points = cell.get_list_item(index=value)
                    if len(vector_points) > 0:
                        # compute distances from current poiunt from them all
                        distances = [haversine((self._values_matrix[0][int(current_position.x)],
                                                self._values_matrix[1][int(current_position.y)]),
                                               list(pos.coords)[0]) * 1000
                                     for pos in vector_points]
                        # compute distances squared
                        distances_updated = [1 / (el * el) for el in distances]

                        all_the_distances[index_vector]["min_value_distace"] = \
                            min(all_the_distances[index_vector]["min_value_distace"], min(distances))
                        all_the_distances[index_vector]["equation_precomputed_value"] += sum(distances_updated)
                    index_vector += 1
            else:
                # only one charge per cell
                centroid_cell = cell.get_centroid()[0]
                distance = haversine((self._values_matrix[0][int(current_position.x)],
                                      self._values_matrix[1][int(current_position.y)]), centroid_cell) * 1000
                distance_updated = 1 / (distance * distance)
                index_vector = 0
                for key, value in self._match_key_index.items():
                    number_of_elements = len(cell.get_list_item(index=value))

                    all_the_distances[index_vector]["min_value_distace"] = \
                        min(all_the_distances[index_vector]["min_value_distace"], distance)
                    all_the_distances[index_vector]["equation_precomputed_value"] += (
                            number_of_elements * distance_updated)
                    index_vector += 1
        return {"distances_per_tag": all_the_distances}

    def find_cell_more_points(self):
        """
        sort cells using number of point contained
        :return:
        """
        id_numbers = []
        for cell in self._list_of_cells.get_all_cells():
            number_of_elements = cell.return_number_elements()
            id_cell = cell.id
            id_numbers.append((id_cell, number_of_elements))
        id_numbers.sort(key=lambda tup: tup[1], reverse=True)

        return id_numbers

    def pre_compute_distance_some_cells(self, order_ids, apf):
        self._log.debug("Precomputing distances from cell most populated to the less one")
        # find current cell
        for idx in order_ids:
            real_id = idx[0]
            # find the current cell
            current_cell = self._list_of_cells.get_cell_from_id(id=real_id)
            borders_matrix = current_cell.get_border_matrix()

            matrix = np.zeros((borders_matrix[1] - borders_matrix[0], borders_matrix[3] - borders_matrix[2]))

            all_the_indexes = []
            real_x = 0
            for x in range(borders_matrix[0], borders_matrix[1]):
                real_y = 0
                list_of_indexes_here = []
                for y in range(borders_matrix[2], borders_matrix[3]):
                    matrix[real_x, real_y] = apf.iloc[x, y]
                    if apf.iloc[x, y] > 25:
                        list_of_indexes_here.append((x, y, real_x, real_y))
                    real_y += 1
                all_the_indexes.append(list_of_indexes_here)
                real_x += 1

            # dataframe_apf = pd.DataFrame.from_records(matrix)
            # # dataframe_apf = dataframe_apf.T
            # plt.pcolor(dataframe_apf)
            # # plt.clim(pd.np.amin(apf), pd.np.amax(apf))
            # plt.colorbar()
            # plt.axis('off')
            # plt.show()

            # number_of_processes = multiprocessing.cpu_count()
            # with Parallel(n_jobs=2, verbose=30) as parallel:
            #     res = parallel(delayed(worker_job_lib)(index, self, real_id) for index in all_the_indexes)

            dic_here = {}
            #
            self._log.debug("there are {} indexes".format(len(all_the_indexes)))
            for i in range(len(all_the_indexes)):
                #     x = all_the_indexes[i][0]
                #     y = all_the_indexes[i][1]
                #     real_x = all_the_indexes[i][2]
                #     real_y = all_the_indexes[i][3]
                #     matrix[real_x, real_y] = self.return_distance_from_point(current_position=Point(x, y))
                # for element in all_the_indexes[i]:
                for j in tqdm.tqdm(range(len(all_the_indexes[i])), desc="Computing the distances {}".format(i)):
                    element = all_the_indexes[i][j]
                    x = element[0]
                    y = element[1]
                    real_x = element[2]
                    real_y = element[3]
                    value = self.precompute_minimum_distance_and_equation(current_position=Point(x, y))
                    name = "{}_{}".format(real_x, real_y)

                    dic_here[name] = value
            total_name = "{}".format(real_id)
            with open('/home/alessandro/GTEA/Helpers/Division/data_on_road/{}_tot_on_road.pickle'.format(total_name),
                      'wb') as handle:
                pickle.dump(dic_here, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def read_precomputed_division_cell(self, path_to_read):
        files_to_find = path_to_read + "/*.pickle"
        all_the_txts = glob.glob(files_to_find)
        #
        huge_one_dict_them_all = {}
        # from tqdm import tqdm
        for file in all_the_txts:
            # file = "14-35_tot.pickle"
            # self._log.debug("Reading file {}".format(file))
            split_of_sentences = file.split("/")
            real_id = split_of_sentences[len(split_of_sentences) - 1].split("_")[0]

            data = pickle.load(open(file, 'rb'))
            # print(data)

            huge_one_dict_them_all[real_id] = data
        # find the current cell
        # current_cell = self._list_of_cells.get_cell_from_id(id=real_id)
        # borders_matrix = current_cell.get_border_matrix()
        #
        # all_the_indexes = []
        # real_x = 0
        # for x in range(borders_matrix[0], borders_matrix[1]):
        #     real_y = 0
        #     list_of_indexes_here = []
        #     for y in range(borders_matrix[2], borders_matrix[3]):
        #         if apf.iloc[x, y] > 0:
        #             list_of_indexes_here.append((x, y, real_x, real_y))
        #         real_y += 1
        #     all_the_indexes.append(list_of_indexes_here)
        #     real_x += 1
        #
        # real_index = split_of_sentences[len(split_of_sentences) - 1].split("_")[1]
        #
        # data = pickle.load(open(file, 'rb'))
        #
        # for key, value in data.items():
        #     real_x = key.split("_")[0]
        #     real_y = key.split("_")[1]
        #     for tag_list in value:
        #

        with open('all_file_together_precomputation.pickle', 'wb') as handle:
            pickle.dump(huge_one_dict_them_all, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def put_precomputed_into_cells(self, apf):
        root = os.path.dirname(os.path.abspath(__file__))
        output_folder = root.replace("Helpers", "Data")
        name_file = "all_file_together_precomputation"
        data = pickle.load(open("{}/{}.pickle".format(output_folder, name_file), 'rb'))
        for key, value in data.items():
            current_cell = self._list_of_cells.get_cell_from_id(id=key)
            borders_matrix = current_cell.get_border_matrix()

            all_the_indexes = []
            real_x = 0
            for x in range(borders_matrix[0], borders_matrix[1]):
                real_y = 0
                list_of_indexes_here = []
                for y in range(borders_matrix[2], borders_matrix[3]):
                    if apf.iloc[x, y] > 0:
                        list_of_indexes_here.append("{}_{}".format(real_x, real_y))
                    real_y += 1
                all_the_indexes.append(list_of_indexes_here)
                real_x += 1

            all_the_keys = list(value.keys())

            all_the_real_keys_ordered = []
            for el in all_the_indexes:
                for sub_el in el:
                    all_the_real_keys_ordered.append(sub_el)

            self._log.debug(
                "key requested {} -> key provided {}".format(len(all_the_real_keys_ordered), len(all_the_keys)))
            if len(all_the_real_keys_ordered) != len(all_the_keys):
                missing_key = []
                for k in all_the_real_keys_ordered:
                    if k not in all_the_keys:
                        missing_key.append(k)
                self._log.debug("missing key: {}".format(missing_key))

            current_cell.matrix = value
        # self._list_of_cells.store_current_list_cells(name="preloaded_division_cell_list")

    def check_if_all_cells_are_present(self, order_ids, apf):

        # file_path = "/Users/alessandrozonta/PycharmProjects/GTEA/Data/division_cell_list_40_by_40.pickle"
        # list_cells = pickle.load(open(file_path, 'rb'))
        for idx in order_ids:
            real_id = idx[0]
            # find the current cell
            current_cell = self._list_of_cells.get_cell_from_id(id=real_id)
            matrix = current_cell.matrix
            borders_matrix = current_cell.get_border_matrix()

            all_the_indexes = []
            real_x = 0
            for x in trange(borders_matrix[0], borders_matrix[1], desc="creation lists"):
                real_y = 0
                for y in range(borders_matrix[2], borders_matrix[3]):
                    if apf.iloc[x, y] > 0:
                        all_the_indexes.append("{}_{}".format(real_x, real_y))

                    real_y += 1
                real_x += 1

            # id_cells = 0
            # id_cell_real = list_cells[id_cells].id
            # while id_cell_real is not real_id:
            #     id_cells += 1
            #     id_cell_real = list_cells[id_cells].id
            try:
                list_positions_loaded = list(matrix.keys())
            except Exception as e:
                list_positions_loaded = []

            if not set(all_the_indexes).issuperset(list_positions_loaded):
                element_missing = np.setdiff1d(all_the_indexes, list_positions_loaded)
                self._log.info("element missing {} for {} cell".format(element_missing, real_id))
            else:
                self._log.info("All the element are correctly loaded for {} cell".format(real_id))

        # all_the_indexes = []
        # for x in trange(0, apf.shape[0], desc="Creation lists.."):
        #     for y in range(0, apf.shape[0]):
        #         if apf.iloc[x, y] > 0:
        #             all_the_indexes.append((x, y))
        # dictionary_positions = {"pos": all_the_indexes}
        # with open('position_with_roads.pickle', 'wb') as handle:
        #     pickle.dump(dictionary_positions, handle, protocol=pickle.HIGHEST_PROTOCOL)

        # dictionary_positions = pickle.load(open('position_with_roads.pickle', 'rb'))
        # all_the_indexes = dictionary_positions["pos"]
        #
        # for x in trange(len(all_the_indexes)):
        #     indexes = all_the_indexes[x]
        #     current_cell_id = self._list_of_cells.find_current_cell_from_matrix_coord(point=Point(indexes[0], indexes[1]))
        #     current_cell = self._list_of_cells.get_cell_from_id(id=current_cell_id)
        #     matrix = current_cell.matrix
        #     if type(matrix) is np.ndarray:
        #         list_positions_loaded = []
        #     else:
        #         list_positions_loaded = list(matrix.keys())
        #     if "{}_{}".format(indexes[0], indexes[1]) not in list_positions_loaded:
        #         with open("id_missing_from_pre_computation.txt", "a") as myfile:
        #             myfile.write("{}_{} \n".format(indexes[0], indexes[1]))
        #         self._log.info("element missing {}_{} for {} cell".format(indexes[0], indexes[1], current_cell_id))

    def check_if_all_present_v0(self, apf):
        list_to_still_precompute = {}
        total_not_present = []
        for cell in self._list_of_cells.get_all_cells():
            borders_matrix = cell.get_border_matrix()

            all_the_indexes = []
            real_x = 0
            for x in trange(borders_matrix[0], borders_matrix[1], desc="creation lists"):
                real_y = 0
                for y in range(borders_matrix[2], borders_matrix[3]):
                    if apf.iloc[x, y] > 0:
                        # all_the_indexes.append("{}_{}".format(real_x, real_y))
                        all_the_indexes.append((x, y))

                    real_y += 1
                real_x += 1

            not_present_elements = []
            for i in trange(len(all_the_indexes), desc="checking cells"):
                current_position = all_the_indexes[i]
                attractions_distances = cell.return_value_attraction(point=current_position, index=0)
                if attractions_distances is None:
                    not_present_elements.append(current_position)
            list_to_still_precompute[cell.id] = not_present_elements
            self._log.debug("cell {} still to precompute: {}".format(cell.id, len(not_present_elements)))
            total_not_present.append(not_present_elements)

        # with open('list_still_to_precompute_v4.pickle', 'wb') as handle:
        #     pickle.dump(list_to_still_precompute, handle, protocol=pickle.HIGHEST_PROTOCOL)

        self._log.debug("still missing: {}".format(total_not_present))

    def precompute_missing_parts(self):
        data_to_load = pickle.load(open('list_still_to_precompute_v4.pickle', 'rb'))
        # split = 7
        # count = 0
        # uber_count = 0
        # dict_here = {}
        # for key, value in data_to_load.items():
        #     if count % split == 0:
        #         with open('small_to_precompute_{}.pickle'.format(uber_count), 'wb') as handle:
        #             pickle.dump(dict_here, handle, protocol=pickle.HIGHEST_PROTOCOL)
        #         uber_count += 1
        #         dict_here = {key: value}
        #     else:
        #         dict_here[key] = value
        #     count += 1

        for key, value in data_to_load.items():
            if key == "39-6":
                dict_cell_precomputed_again = {}
                current_cell = self._list_of_cells.get_cell_from_id(id=key)
                from tqdm import tqdm
                for current_position in tqdm(value, desc="Computing cell {}".format(key)):
                    attractions_distances = current_cell.return_value_attraction(point=current_position, index=0)
                    if attractions_distances is None:
                        attractions_distances = self.precompute_minimum_distance_and_equation(
                            current_position=Point(current_position[0], current_position[1]))

                        # name_in_index = self._indexing.get("{}_{}".format(point.x, point.y))
                        # current_cell.add_value_back_to_matrix(data=attractions_distances, point=Point(current_position[0], current_position[1]))
                        dict_cell_precomputed_again[
                            "{}_{}".format(current_position[0], current_position[1])] = attractions_distances
                with open('third_wave_precomputed_{}.pickle'.format(key), 'wb') as handle:
                    pickle.dump(dict_cell_precomputed_again, handle, protocol=pickle.HIGHEST_PROTOCOL)

        # self._log.info("storing data")
        # self._list_of_cells.store_current_list_cells(name="last_update_all_missing")

    def unite_the_divided(self):
        path = "/Users/alessandrozonta/PycharmProjects/GTEA/Helpers"
        files_to_find = path + "/third_wave_precomputed_*.pickle"
        all_the_files = glob.glob(files_to_find)
        for f in all_the_files:
            data_to_load = pickle.load(open(f, 'rb'))
            name_file_complete = f.split("/")
            last_word = name_file_complete[len(name_file_complete) - 1].split("_")
            id_cell = last_word[len(last_word) - 1].replace(".pickle", "")

            current_cell = self._list_of_cells.get_cell_from_id(id=id_cell)
            if current_cell is not None:
                for key, value in data_to_load.items():
                    two_elements = key.split("_")

                    current_cell.add_value_back_to_matrix(data=value,
                                                          point=Point(int(two_elements[0]), int(two_elements[1])))

        self._log.info("storing data")
        self._list_of_cells.store_current_list_cells(name="update_from_big_mac_v1")

    def get_apf(self):
        return self._apf

    def get_is_updated(self):
        return self._has_been_updated

    def keep_only_points_on_street(self, points):
        """
        Check if the points provided are on a route
        :param apf: Dataframe describing the routing system
        :param points: list of points to check
        :return: list of points from the input list that are actually on a route
        """
        points_on_street = []
        for p in points:
            id_current_cell = self._list_of_cells.find_current_cell_from_matrix_coord(point=p)
            cell = self._list_of_cells.get_cell_from_id(id=id_current_cell)
            if cell.check_if_on_a_road(point=p):
                points_on_street.append(p)
        return points_on_street

    def store_again_all_the_data(self):
        self._list_of_cells.store_current_list_cells(name="division_cell_list_updated")

    def store_everything_on_mmap_file(self):
        max_x_range = 0
        max_y_range = 0
        for cell in self._list_of_cells.get_all_cells():
            borders_matrix = cell.get_border_matrix()

            # self._min_x_cell, self._max_x_cell, self._min_y_cell, self._max_y_cell
            x_range = borders_matrix[1] - borders_matrix[0]
            y_range = borders_matrix[3] - borders_matrix[2]
            max_x_range = max(max_x_range, x_range)
            max_y_range = max(max_y_range, y_range)

        number_of_tag = 6
        info_typology = 2
        number_of_total_cells = len(self._list_of_cells.get_all_cells())
        # array = np.zeros((max_x_range, max_y_range, number_of_tag, info_typology, number_of_total_cells), dtype='float32')
        print("({},{},{},{},{})".format(max_x_range, max_y_range, number_of_tag, info_typology, number_of_total_cells))
        # array.fill(np.nan)
        # for i in trange(number_of_total_cells):
        #     cell = self._list_of_cells.get_all_cells()[i]
        #     matrix = cell.matrix
        #     for key, value in matrix.items():
        #         if key is not None:
        #             real_indexes = key.split("_")
        #             here_x = int(real_indexes[0])
        #             here_y = int(real_indexes[1])
        #             print("{}_{}".format(here_x, here_y))
        #             list_values = value["distances_per_tag"]
        #             for j in range(len(list_values)):
        #                 inside_dict = list_values[j]
        # array[here_x, here_y, j, 0, i] = inside_dict["min_value_distace"]
        # array[here_x, here_y, j, 1, i] = inside_dict["equation_precomputed_value"]

        # filename = "test_cells_to_mmap.dat"
        # fp = np.memmap(filename, dtype='float32', mode='w+', shape=(max_x_range, max_y_range, number_of_tag, info_typology, number_of_total_cells))
        # fp[:] = array[:]
        # del fp

    def drop_data_from_all_the_list_saved(self):
        for cell in self._list_of_cells.get_all_cells():
            cell.matrix = None
            cell._on_road = None
            cell._points = None
        self._list_of_cells.store_current_list_cells(name="slim_version_of_cells")

    def change_type_of_indexing(self):
        # too big
        for cell in self._list_of_cells.get_all_cells():
            indexing = cell._indexing
            new_indexing = {}
            for key, value in indexing.items():
                two_values = value.split("_")
                new_value = (int(two_values[0]), int(two_values[1]))
                new_indexing[key] = new_value
            cell._indexing = new_indexing
        self._list_of_cells.store_current_list_cells(name="new_indexing_cells")

    def load_mmap_file_and_store_missing_points(self):
        path = "/Volumes/Cthulhu/GTEA/cell_pre_computation_inside_road/"
        files_to_find = path + "/*.pickle"
        all_the_files = glob.glob(files_to_find)

        max_x_range = 154
        max_y_range = 155
        # for cell in self._list_of_cells.get_all_cells():
        #     borders_matrix = cell.get_border_matrix()
        #
        #     # self._min_x_cell, self._max_x_cell, self._min_y_cell, self._max_y_cell
        #     x_range = borders_matrix[1] - borders_matrix[0]
        #     y_range = borders_matrix[3] - borders_matrix[2]
        #     max_x_range = max(max_x_range, x_range)
        #     max_y_range = max(max_y_range, y_range)

        number_of_tag = 6
        info_typology = 2
        number_of_total_cells = len(self._list_of_cells.get_all_cells())

        path = "/Volumes/Cthulhu/GTEA/cell_pre_computation_outside_road/cell_data_to_mmap.dat"
        matrix = np.memmap(path, dtype='float32', mode='r+',
                           shape=(max_x_range, max_y_range, number_of_tag, info_typology, number_of_total_cells))

        for f in all_the_files:
            name_file = f.split("/")[-1].split("_")[0]

            cell = self._list_of_cells.get_cell_from_id(id=name_file)
            index_cell = cell.index

            data = pickle.load(open(f, 'rb'))
            for key, value in tqdm.tqdm(data.items(), desc="Adding value to {}".format(index_cell)):
                # key is the position -> need to retrieve values
                here_x = int(key.split("_")[0])
                here_y = int(key.split("_")[1])

                for tag in range(len(value["distances_per_tag"])):
                    matrix[here_x, here_y, tag, 0, index_cell] = value["distances_per_tag"][tag]["min_value_distace"]
                    matrix[here_x, here_y, tag, 1, index_cell] = value["distances_per_tag"][tag][
                        "equation_precomputed_value"]

    def return_charge_from_point_single(self, current_position, genome, genome_meaning, K):
        """
        return the charge from the current points using the cells system
        :param current_position: current position
        :param genome: genome evolved
        :param genome_meaning: meaning if every pos of the genome
        :param K: constant for the computation of the charge
        :return: double total charge
        """
        current_cell_id = self._list_of_cells.find_current_cell_from_matrix_coord(point=current_position)
        total_charge = []
        cell = self._list_of_cells.get_cell_from_id(id=current_cell_id)

        index = 0
        for key, value in self._match_key_index.items():

            # get the charge
            charge = genome[genome_meaning.from_genome_to_value_describing_object(name_object=key)]

            # add to the total charge
            attractions_distances = cell.return_value_attraction(point=[current_position.x, current_position.y],
                                                                 index=index)
            if attractions_distances is None:
                raise ValueError()

            here_charge = K * charge * attractions_distances
            total_charge.append(attractions_distances)

            index += 1

        return total_charge

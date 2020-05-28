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
import logging
import multiprocessing
from sklearn.externals.joblib import Parallel, delayed

from src.Division.ComputeDivision import SubMatrix
from src.Individual.GenerativeIndividual import TrajectoryGeneration
from src.Loaders.GenomePhenome import GenomeMeaning
from src.Loaders.LoadAPF import LoadAPF
from src.Loaders.PlacesOnRoute import FindPlacesOnRoutes
from src.Settings.args import args


def worker_job_lib(individual, idx):
    distances, tra, real_tra, path = individual.create_trajectory(random_seed=10, idx=idx)
    return (distances, tra, real_tra, path)


class Controller(object):
    def __init__(self, path_trajectories, path_apf, name_log, log_to_file=False, log_to_console=True):
        self._path_trajectories = path_trajectories
        self._path_apf = path_apf
        self._name_exp = name_log
        self._logger = logging.getLogger(name_log)
        self._logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        if log_to_console:
            # create console handler
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(formatter)
            # add the handlers to the logger
            self._logger.addHandler(ch)

        if log_to_file:
            # create file handler
            fh = logging.FileHandler(name_log + '.log')
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)
            # add the handlers to the logger
            self._logger.addHandler(fh)

        # need to load the controller from file saved -> path -> name I already know
        # decide which generation to use -> last? (0) or something before? (-1,....,-N)
        # load the controller and assign it to the generator
        # random position and taac, generate tra and save it
        self._list_genome = None

        self._loader_apf = LoadAPF(path=self._path_apf, logger=self._logger)
        self._loader_apf.load_apf_only_routing_system()
        self._loader_apf.match_index_with_coordinates()
        self._loader_genome_meaning = GenomeMeaning(logger=self._logger, granularity=0)
        self._loader_genome_meaning.load_data(test=False)

        self._sub_matrix = SubMatrix(log=self._logger, apf=self._loader_apf.apf,
                                     list_points=self._loader_genome_meaning.name_and_position,
                                     values_matrix=(self._loader_apf.x_values, self._loader_apf.y_values),
                                     save_and_store=True)
        self._sub_matrix.divide_into_cells(x_division=40, y_division=40)

        self._pre_loaded_points = FindPlacesOnRoutes(logger=self._logger)
        self._pre_loaded_points.load_preloaded_position()

    def set_vector_data(self, vector_data):
        """
        Read data from file and load the controller
        :param vector_data:
        :return:
        """
        self._list_genome = vector_data

    def initialise_individual_and_run(self, save_path, how_many, version="0"):
        individual = TrajectoryGeneration(length=len(self._list_genome) - 5, logger=None,
                                          genotype=self._list_genome,
                                          values_matrix=(self._loader_apf.x_values, self._loader_apf.y_values),
                                          apf=self._loader_apf.apf, genome_meaning=self._loader_genome_meaning,
                                          pre_matrix=self._sub_matrix,
                                          type_of_generator=args.type_generator,
                                          type_astar=args.type_astar,
                                          pre_loaded_points=self._pre_loaded_points)

        self._logger.debug("Generating Trajectories")
        results = []
        number_of_processes = multiprocessing.cpu_count() - 1
        if how_many < number_of_processes:
            number_of_processes = how_many
        with Parallel(n_jobs=number_of_processes, verbose=30) as parallel:
            res = parallel(delayed(worker_job_lib)(individual, i) for i in range(how_many))
            results.append(res)

        # distances, tra, real_tra, path, preloaded_points
        total_tra = []
        # total_vector_distances = []
        total_real_tra = []
        total_paths = []
        for trial in results[0]:
            total_tra.append(trial[1])
            # total_vector_distances.append(trial[0])
            total_real_tra.append(trial[2])
            total_paths.append(trial[3])

        for el in total_real_tra:
            str = ""
            for point in el:
                str += "[ " + point.print() + " ] "
            tra_path_real = save_path + "real_trajectories_{}.txt".format(version)
            with open(tra_path_real, "a") as myfile:
                myfile.write("{} \n".format(str))

        for el in total_tra:
            str = ""
            for point in el:
                str += "[ " + point.print() + " ] "
            tra_path_real = save_path + "tra_trajectories_{}.txt".format(version)
            with open(tra_path_real, "a") as myfile:
                myfile.write("{} \n".format(str))

        for el in total_paths:
            str = ""
            for point in el:
                str += "[ " + point.print() + " ] "
            tra_path_real = save_path + "paths_trajectories_{}.txt".format(version)
            with open(tra_path_real, "a") as myfile:
                myfile.write("{} \n".format(str))

        self._logger.debug("Trajectories generated")
        if self._sub_matrix.get_is_updated():
            self._sub_matrix.store_again_all_the_data()

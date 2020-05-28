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
import numpy as np
import uuid


class Individual(object):
    """
    Implementation of a base individual of the EA algorithm
    """
    def __init__(self, length, logger=None, genotype=None):
        self.id = uuid.uuid4()
        self.genome = []
        self.fitness = 0
        self._length = length
        if genotype is None:
            # for i in range(length):
            #     self.genome.append(random_wrapper_uniform(lower_bound=-4.0, upper_bound=4.0))
            self.genome = [random_wrapper_uniform(lower_bound=-4.0, upper_bound=4.0) for i in range(length)]
        else:
            self.genome = genotype
        self.step_size = random_wrapper_uniform(lower_bound=0.0001, upper_bound=0.1)
        self._log = logger

        # generating a random number with python is super slow.
        # to improve the efficiency I generate a vector long 5000 filled with random number
        # if the vector has less than 300 number I add them to the list
        self._random_normalvariate_numbers = []
        self.create_random_numbers_for_efficiency()

    def mutate(self):
        """
        Mutation operator

        it mutates the individual

        :return: nothing
        """
        if len(self._random_normalvariate_numbers) < len(self.genome) + 2:
            self.create_random_numbers_for_efficiency()

        rnd = self._random_normalvariate_numbers.pop()
        alpha = 1 / np.math.pow(self._length, 0.5)
        self.step_size = self.step_size * np.math.exp(alpha * rnd)
        if self.step_size < 0.0001:
            self.step_size = 0.0001
        for i in range(len(self.genome)):
            rnd = self._random_normalvariate_numbers.pop()
            self.genome[i] = self.genome[i] + self.step_size * rnd

    def increase_fitness(self, value):
        """
        Pretty straightforward method
        :param value: how much I am increasing the fitness
        :return: nothing
        """
        self.fitness += value

    def create_random_numbers_for_efficiency(self):
        """
        generating a random number with python is super slow.
        to improve the efficiency I generate a vector long 100000 filled with random number
        if the vector has less than 300 number I add them to the list
        :return:
        """
        how_many_i_have = len(self._random_normalvariate_numbers)
        how_many_i_need = 100000 - how_many_i_have
        list_appo = random_wrapper_normalvariate(mean=0, std=1, elements=how_many_i_need).tolist()
        self._random_normalvariate_numbers.extend(list_appo)

    def remove_log(self):
        """
        Remove log handler
        :return:
        """
        self._log = None

    def reset_fitness(self):
        """
        set to zero the fitness
        :return:
        """
        self.fitness = 0

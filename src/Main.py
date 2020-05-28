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
import os

from src.Experiment.Controller import Controller
from src.Loaders.Attractiveness import ForcedAttractiveness
from src.Settings.args import args

if __name__ == '__main__':
    tra_path = args.data_path + args.tra_name
    apf_path = args.data_path + args.apf_name

    a = Controller(path_trajectories=tra_path, path_apf=apf_path,
                   name_log=args.name_exp,
                   log_to_file=args.log_to_file,
                   log_to_console=args.log_to_console)

    d = ForcedAttractiveness()
    v = d.v

    name_counter = 0
    for vector in v:
        try:
            name = "generate_tra_per_force"
            path = "{}/{}_exp{}/".format(args.output_path, name, name_counter)
            args.name_exp = "{}_exp{}".format(name, name_counter)
            os.mkdir(path)
        except OSError:
            print("Creation of the directory %s failed" % path)
        else:
            print("Successfully created the directory %s " % path)

        a.set_vector_data(vector_data=vector)
        a.initialise_individual_and_run(save_path=path, how_many=args.n_tra_generated)

        name_counter += 1

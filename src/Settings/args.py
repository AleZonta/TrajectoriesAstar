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
import argparse


def prepare_parser():
    parser = argparse.ArgumentParser(description="awe")

    # general settings
    parser.add_argument("--north", type=float, default=46.3)
    parser.add_argument("--south", type=float, default=45.8)
    parser.add_argument("--east", type=float, default=14.8)
    parser.add_argument("--west", type=float, default=14.1)
    parser.add_argument("--type_generator", default="astar")
    parser.add_argument("--type_astar", type=int, default=1,
                        help="0 is mostly distance, 1 evolved average, 2 mostly apf, 3 real Astar")
    parser.add_argument("--tra_name", default="small_sport.json")
    parser.add_argument("--apf_name", default="the_right_one.csv")
    parser.add_argument("--data_path", default="")
    parser.add_argument("--output_path", default="")
    parser.add_argument("--name_exp", default="test_astar")
    parser.add_argument("--log_to_file", action='store_true')
    parser.add_argument("--log_to_console", action='store_true')
    parser.add_argument("--n_tra_generated", type=int, default=50)

    return parser


parser = prepare_parser()
args = parser.parse_args()

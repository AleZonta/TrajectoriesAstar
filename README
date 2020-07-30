# Trajectories-Astar. Towards a human-like movements generator based on environmental features

Trajectories-Astar is a Python library implementing the A* experiment present in the paper "Towards a human-like movements generator based on environmental features".
It implements the normal two modifications of the normal A* algorithm employed to generate trajectories conditioned on environmental featurs.

## Requirements
 Tested only with `Python 3.6`
* `numpy==1.18.5`
* `matplotlib==2.2.2`
* `haversine==2.2.0`
* `scipy==1.1.0`
* `Shapely==1.6.4.post2`
* `joblib==0.16.0`
* `seaborn==0.9.0`
* `tqdm==4.43.0`
* `folium==0.11.0`
* `feather-format==0.4.1`
* `pandas==0.23.3`
* `pyarrow==0.13.0`
* `tables==3.6.1`

## Data
Download the dataset used from [here](https://doi.org/10.5281/zenodo.3964449) and place it in data.
Update path on the setting file accordingly

## Run the experiments
* check if all the path are corrects in the settings of the various scripts
* to generate new trajectories run src/Main.py
* use `--type_astar` to select which typology of A* you want to run. 0 for the attraction based, and 1 for the fitness based
* use `--n_tra_generated` to define how many trajectories to generate. By default the system support multiprocessing
* use `--total_distance_to_travel` to define how long you want the trajectories to be. There is no limit for this value
* use `--point_distancel` if you want to modify the behaviour of the fitness based A*. Check `args.py` to see what are the selection for this argument


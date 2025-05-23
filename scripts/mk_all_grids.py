import yaml
import os
import numpy as np
import psf_grid_utils as pgu
from multiprocessing import Pool

outdir = os.getenv("psf_grid_data_dir")
if outdir is None:
    raise RuntimeError("psf_grid_data_dir environment variable has not been set")

github_dir = os.getenv("github_dir")
if github_dir is None:
    raise RuntimeError("github_dir environment variable has not been set")

conf_file = os.path.join(github_dir, "psf_grids/data/psf_grid_config.yaml")
with open(conf_file) as f:
    grid_conf = yaml.safe_load(f)

conf_file = os.path.join(github_dir, "grism_sim/data/grizli_config.yaml")
with open(conf_file) as f:
    grizli_conf = yaml.safe_load(f)

bins = np.linspace(grizli_conf["minlam"], grizli_conf["maxlam"], grizli_conf["npsfs"] + 1)

params = []
for det_num in range(1, 19):
     for wave in bins[:-1]:
          params.append([det_num, wave])

def mk_grid(args):
    pgu.save_one_grid(args[0], args[1], outdir, fov_pixels=grid_conf["fov_pixels"], overwrite=True)

if __name__=="__main__":
    nproc = 90
    with Pool(processes=nproc) as pool:
        res = pool.map(mk_grid, params)

    if np.any(res):
        print("Unexpected result. Potential failure")
        print(res)

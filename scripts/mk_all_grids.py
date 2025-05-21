import yaml
import os
import numpy as np
import psf_grid_utils as pgu
from multiprocessing import Pool

github_dir = os.getenv("github_dir")
outdir = os.path.join(github_dir, "psf_grids/data")

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

if __name__ == "__main__":
    nproc = 9
    with Pool(processes=nproc) as pool:
        res = pool.map(mk_grid, params)

    print(res)

    if np.any(res):
        print("Potential Fail. See results")

# for wavelength in bins:
#     print(f"""
#           starting {wavelength}
#           """)
    # pgu.save_all_grids(wavelength, outdir, fov_pixels=grid_conf["fov_pixels"], overwrite=True)
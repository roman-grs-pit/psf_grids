import logging

logging.basicConfig(filename="log.txt",
                    filemode='a',
                    format='%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)

logger.info("STARTING NEW FILE HERE")

logger.info("Beginning Imports")

import yaml
logger.info("Imported yaml")
import os
logger.info("Imported os")
import numpy as np
logger.info("Imported numpy")
import psf_grid_utils as pgu
logger.info("Imported psf_grid_utils")
from multiprocessing import Pool
logger.info("Imported multiprocessing")

psf_grid_dir = os.getenv("psf_grid_dir")
outdir = os.path.join(psf_grid_dir, "psf_grids/data")

logger.info("Read psf_grid_dir environment variable")

github_dir = os.getenv("github_dir")

logger.info("Read github_dir environment variable")

conf_file = os.path.join(psf_grid_dir, "psf_grids/data/psf_grid_config.yaml")
with open(conf_file) as f:
        grid_conf = yaml.safe_load(f)

logger.info("Loaded psf_grid_config.yaml")

conf_file = os.path.join(github_dir, "grism_sim/data/grizli_config.yaml")
with open(conf_file) as f:
    grizli_conf = yaml.safe_load(f)

logger.info("Loaded grizli_config.yaml")

bins = np.linspace(grizli_conf["minlam"], grizli_conf["maxlam"], grizli_conf["npsfs"] + 1)

logger.info("Defined bins")

params = []
for det_num in range(1, 19):
     for wave in bins[:-1]:
          params.append([det_num, wave])

logger.info("Defined param pairs")

def mk_grid(args):
    pgu.save_one_grid(args[0], args[1], outdir, fov_pixels=grid_conf["fov_pixels"], overwrite=True)

logger.info("Defined mk_grid function.")

if __name__=="__main__":
    nproc = 90
    with Pool(processes=nproc) as pool:
        res = pool.map(mk_grid, params)
    
    logger.info("Pool created")

    if np.any(res):
        logger.warning("Unexpected result. Potential failure")


# for wavelength in bins:
#     print(f"""
#           starting {wavelength}
#           """)
    # pgu.save_all_grids(wavelength, outdir, fov_pixels=grid_conf["fov_pixels"], overwrite=True)
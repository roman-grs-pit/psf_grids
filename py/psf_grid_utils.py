import os
import webbpsf
import subprocess
from astropy.io import fits

github_dir_env=os.getenv('github_dir')
if github_dir_env is None:
    print('github_dir environment variable has not been set, will cause problems if not explicitly set in function calss')

wfi = webbpsf.WFI()

def create_psf_grid(wavelength=1.5e-6, fov_pixels=364, det="SCA01"):
    """
    Returns a monochromatic photutils GriddedPSFModel for a single detector.
    """
    wfi.detector = det
    grid = wfi.psf_grid(all_detectors=False, use_detsampled_psf=True, monochromatic=wavelength, fov_pixels=fov_pixels)
    return grid

def load_psf_grid(grid_file, github_dir=github_dir_env):
    """
    Reads in a saved GriddedPSFModel fits file. Returns that file.
    """
    filepath = os.path.join(github_dir, grid_file)
    grid = webbpsf.utils.to_griddedpsfmodel(filepath)
    return grid

def save_grid_all_detectors(wavelength, outdir, fov_pixels=364, **kwargs):
    """
    Computes and saves GriddedPSFModel fits files for all detectors at a given wavelength. 
    Follows naming scheme: 
    {instrument}_{filter}_{fovp}_{wavelength}_{det}.fits
    e.g. wfi_grism0_fovp364_10000_sca01.fits
    """

    outfile = f"{wfi.name}_{wfi.filter}_fovp{fov_pixels}_{wavelength}".lower() #_det.fits is added automatically

    wfi.psf_grid(all_detectors=True, use_detsampled_psf=True, monochromatic=wavelength*1e-10, fov_pixels=fov_pixels, 
                save=True, outdir=outdir, outfile=outfile, overwrite=True, **kwargs)
    
    return 0

def add_git_sha_heder(filepath):

    gitsha = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("ascii").strip()

    file = fits.open(filepath)
    
    file[0].header["gitsha"] = gitsha
    file.writeto(filepath, overwrite=True)
    file.close()

    return 0

def check_version(filepath):

    gitsha = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("ascii").strip()

    file = fits.open(filepath)

    try:
        if file[0].header["gitsha"] == gitsha:
            return 0
        else:
            return 1
    except KeyError:
        return 2
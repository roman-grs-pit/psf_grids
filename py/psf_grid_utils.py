import os
from astropy.io import fits
import json
import hashlib
import image_utils as iu
import time

try:
    import stpsf
except:
    import webbpsf as stpsf

psf_grid_data_read=os.getenv('psf_grid_data_read')
if psf_grid_data_read is None:
    print('psf_grid_data_read environment variable has not been set')

wfi = stpsf.WFI()
wfi.filter = "GRISM1"

def switch_filter(filter_name):
    """
    Switched to the given filter
    """

    wfi.filter = filter_name

    print(wfi.filter)
    
    return 0 

def load_psf_grid(grid_file, psf_grid_data_read=psf_grid_data_read):
    """
    Reads in a saved GriddedPSFModel fits file. Returns that file.
    """
    filepath = os.path.join(psf_grid_data_read, grid_file)
    grid = stpsf.utils.to_griddedpsfmodel(filepath)
    return grid

def save_one_grid(det_num, wavelength, outdir, fov_pixels=364, overwrite=False, **kwargs):
    """
    Computes and saves GriddedPSFModel fits files for a single detector at a given
    wavelength. Creates a detector's fits file and modifies it's header with args
    and version hash.

    Follows naming scheme: 
    {instrument}_{filter}_{fovp}_wave{wavelength}_{det}.fits
    e.g. wfi_grism1_fovp364_wave10000_sca01.fits
    """
    
    __KWARGS_USED = False
    if kwargs:
        __KWARGS_USED = True

    print(f"\nGenerating PSF Grid fits file for SCA{det_num:02} at {wavelength:.0f}\u212b...")
    create_grid_one_detector(det_num, wavelength, fov_pixels=fov_pixels, save=True, outdir=outdir, overwrite=overwrite, **kwargs)
    
    filename = f"{wfi.name}_{wfi.filter}_fovp{fov_pixels}_wave{wavelength:.0f}_SCA{det_num:02}.fits".lower()
    filepath = os.path.join(outdir, filename)

    print(f"Adding version info to header for SCA{det_num:02} at {wavelength:.0f}\u212b...")
    add_version_info(filepath, __KWARGS_USED, **kwargs)

    print("PSF Grid fits generation and versioning successful!")

    return 0

def create_grid_one_detector(det_num, wavelength, fov_pixels=364, save=False, outdir=None, overwrite=False, **kwargs):
    """
    Computes and saves GriddedPSFModel fits file for a single detector at a given
    wavelength. Does not modify the header with version info.

    Follows naming scheme: 
    {instrument}_{filter}_{fovp}_wave{wavelength}_{det}.fits
    e.g. wfi_grism1_fovp364_wave10000_sca01.fits
    """

    detector = "SCA{:02}".format(det_num)
    wfi.detector = detector

    if save:
        outfile = f"{wfi.name}_{wfi.filter}_fovp{fov_pixels}_wave{wavelength:.0f}".lower() #_det.fits is added automatically

        wfi.psf_grid(all_detectors=False, use_detsampled_psf=True, monochromatic=wavelength*1e-10, fov_pixels=fov_pixels,
                     save=True, outdir=outdir, outfile=outfile, overwrite=overwrite, **kwargs)

        return 0

    return wfi.psf_grid(all_detectors=False, use_detsampled_psf=True, monochromatic=wavelength*1e-10, fov_pixels=fov_pixels,
                        save=False, **kwargs)
    

def dict_hash(dict):
    """
    Return a SHA256 hash of a dictionary, order-independent.
    """

    # Convert dictionary to a JSON string with sorted keys
    dict_json = json.dumps(dict, sort_keys=True, separators=(',', ':'))
    # Encode and hash
    version_hash = hashlib.sha256(dict_json.encode('utf-8')).hexdigest()

    return version_hash

def add_version_info(filepath, kwargs_flag, ext=0, **kwargs):
    """
    Opens the fits located at {filepath}. Save the kwargs and stpsf version into
    the header. Hash kwarg dictionary and save hash for easy version checking.
    """

    # Track stpsf version
    kwargs["stpsfver"] = stpsf.__version__
    version_hash = dict_hash(kwargs) # Acquire version_hash
    kwargs["verhash"] = version_hash # Put version hash in kwargs
    kwargs["kwargsuse"] = kwargs_flag # Set kwargs flag

    file = try_wait_loop(fits.open, filepath)
    header = file[ext].header

    # write all kwargs to header
    for key, value in kwargs.items():
        header[key] = value

    file[ext].header = header
    file.writeto(filepath, overwrite=True)
    file.close()
    
    return 0

def check_version(filename, ext=0, **kwargs):
    """
    Opens the fits located at {filepath}. Computes expected version_hash value from
    kwargs. Checks value against header. If values are equal, returns a 0. Else,
    prints header and returns a 1.
    """

    filepath = os.path.join(psf_grid_data_read, filename)
    
    kwargs["stpsfver"] = stpsf.__version__
    expected_hash = dict_hash(kwargs)

    file = try_wait_loop(fits.open, filepath)
    header = file[ext].header

    if header["verhash"] == expected_hash:
        print(f"Version hash matches expected value")
        return 0
    else:
        print(header.tostring(sep='\n'))
        print(f"\n\033[93mVersion hash does not match\033[0m\n")
        return 1

def try_wait_loop(func, *args, max_attempts=3, wait=5, **kwargs):
    """
    Attempt to call func using args and kwargs. Upon a fail, wait som time and try
    again. Upon {max_attempts} number of fails, raise Exception. Used when reading
    files recently written on NERSC.

    Parameters
    ----------
    func: callable
        Function or other callable to attempt calling
    max_attempts: int, optional
        Maximum number of attempts before raising exception. default: 3
    wait: float, optional
        Seconds to wait upon failure before retrying. default: 5
    """
    attempt = 0
    while attempt < max_attempts:
        try:
            res = func(*args, **kwargs)
            break
        except Exception as e:
            attempt += 1 
            if attempt < max_attempts:
                print(f"{func.__name__} failed. Waiting {wait} and retrying: {attempt}/{max_attempts}")
                time.sleep(wait)
            else:
                print(f"{func.__name__} failed. Maximum retries exceeded: {max_attempts}")
                raise e
    
    return res
# uses pyird v1.1, Hajime Kawahara

#select y or h
band = "y"  #'h' or 'y'

#if you do not want to show plots, please comment out the following lines
#import matplotlib
#matplotlib.use("Agg")

import pathlib

# STEP 0 Settings
## data directories definition
basedir = pathlib.Path("~/subaru/202501").expanduser()

# same as HK's flat/dark data
datadir_flat = basedir / "data/20250114/"
datadir_dark = {}
datadir_dark["h"] = basedir / "data/Kawahara20250113/dark/H-band"
datadir_dark["y"] = basedir / "data/Kawahara20250113/dark/YJ-band"

# different from HK's
datadir_thar = {}
datadir_thar["h"] = basedir / "data/Kawashima_S24B_123/H-band/ThAr-star"
datadir_thar["y"] = basedir / "data/Kawashima_S24B_123/YJ-band/ThAr-star"

datadir = basedir / "data/20250109/"
anadir = basedir / "anaird2501/reduction_yk/"

mmf = "mmf2"  #'mmf1' (comb fiber) or 'mmf2' (star fiber)
readout_noise_mode = "default"

## file numbers of fits files (last five digits)
fitsid_flat = list(range(76062, 76154, 2)) + list(
    range(76158, 76168, 2)
)  # should not use 76154, 76156
fitsid_dark = [23483]  # 1200sec

# different from HK's, same fitsid for H and YJ (IRDAD = H , IRDBD=YJ)
fitsid_thar = list(range(23478, 23483))

fitsid_target = list(range(76014, 76044, 2))

# STEP 1: Preprocessing
## aperture extraction
from pyird.utils import irdstream

flat = irdstream.Stream2D("flat", datadir_flat, anadir, fitsid=fitsid_flat, band=band)

if band == "h":
    trace_mmf = flat.aptrace(cutrow=1500, nap=21)
elif band == "y":
    trace_mmf = flat.aptrace(cutrow=1000, nap=51)

## trace mask
trace_mask = trace_mmf.mask()

from pyird.image.bias import bias_subtract_image
from pyird.image.hotpix import identify_hotpix_sigclip

## DARK
if band == "h":
    rawtag = "IRDAD000"
elif band == "y":
    rawtag = "IRDBD000"
dark = irdstream.Stream2D(
    "dark", datadir_dark[band], anadir, fitsid=fitsid_dark, rawtag=rawtag, band=band
)
median_image = dark.immedian()
im_subbias = bias_subtract_image(median_image)
hotpix_mask = identify_hotpix_sigclip(im_subbias)

## ThAr
thar = irdstream.Stream2D(
    "thar", datadir_thar[band], anadir, fitsid=fitsid_thar, rawtag=rawtag, band=band
)
thar.trace = trace_mmf
thar.clean_pattern(
    trace_mask=trace_mask, extin="", extout="_cp", hotpix_mask=hotpix_mask
)
thar.calibrate_wavelength()

## Normalizes Flat
flat = irdstream.Stream2D(
    "flat_star", datadir_flat, anadir, fitsid=fitsid_flat, band=band
)
flat.trace = trace_mmf

## Removes noise pattern
flat.clean_pattern(
    trace_mask=trace_mask, extin="", extout="_cp", hotpix_mask=hotpix_mask
)
flat.imcomb = True  # median combine

## Extracts 1D spectrum
flat.flatten(hotpix_mask=hotpix_mask)

## Flat spectrum normalized in each pixel within an aperture
df_flatn = flat.apnormalize()

# STEP2: 1D Spectrum Extraction
##--------FOR TARGET--------#
target = {}
## Settings
target = irdstream.Stream2D(
    "targets",
    datadir,
    anadir,
    fitsid=fitsid_target,
    band=band,
)
target.info = True  # show detailed info
target.trace = trace_mmf
# removes noise pattern (makes _cp fits files)
target.clean_pattern(
    trace_mask=trace_mask, extin="", extout="_cp", hotpix_mask=hotpix_mask
)
## Flat fielding
target.apext_flatfield(df_flatn, hotpix_mask=hotpix_mask)
target.dispcor(master_path=thar.anadir, extin="_flnhp")

# Blaze function
flat.apext_flatfield(df_flatn, hotpix_mask=hotpix_mask)
flat.dispcor(master_path=thar.anadir)

# Normalizes the target spectrum
target.normalize1D(master_path=flat.anadir, readout_noise_mode=readout_noise_mode)

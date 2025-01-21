# uses pyird v1.1, Hajime Kawahara

import pathlib

# STEP 0 Settings
## data directories definition
basedir = pathlib.Path("~/subaru/202501").expanduser()

datadir_flat = basedir / "data/20250114/"
datadir_dark = {}
datadir_dark["h"] = basedir / "data/Kawahara20250113/dark/H-band"
datadir_dark["y"] = basedir / "data/Kawahara20250113/dark/YJ-band"


dayarr = ["day1", "day2", "day3"]
datadir = {}
datadir["day1"] = basedir / "data/20250114/"
datadir["day2"] = basedir / "data/20250115/"
datadir["day3"] = basedir / "data/20250116/"

anadir = basedir / "anaird2501/reduction/"

band = "h"  #'h' or 'y'
mmf = "mmf2"  #'mmf1' (comb fiber) or 'mmf2' (star fiber)
readout_noise_mode = "default"

## file numbers of fits files (last five digits)
fitsid_flat = list(range(76062, 76154, 2)) + list(
    range(76158, 76168, 2)
)  # should not use 76154, 76156
fitsid_dark = [23483]  # 1200sec

fitsid_thar = {}
fitsid_thar["day1"] = list(range(76178, 76188, 2))
fitsid_thar["day2"] = list(range(76228, 76238, 2))
fitsid_thar["day3"] = list(range(76278, 76288, 2))

fitsid_target = {}
fitsid_target["day1"] = list(range(76054, 76062, 2))
fitsid_target["day2"] = list(range(76192, 76218, 2))
fitsid_target["day3"] = list(range(76240, 76268, 2))

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

## ThAr day1-day3
thar = {}
for day in dayarr:
    thar[day] = irdstream.Stream2D(
        "thar_" + str(day), datadir[day], anadir, fitsid=fitsid_thar[day], band=band
    )
    thar[day].trace = trace_mmf
    thar[day].clean_pattern(
        trace_mask=trace_mask, extin="", extout="_cp", hotpix_mask=hotpix_mask
    )
    thar[day].calibrate_wavelength()

## Normalizes Flat
flat = irdstream.Stream2D("flat_star", datadir_flat, anadir, fitsid = fitsid_flat, band=band)
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
for day in dayarr:
    print("##########", day, "##########")
    ## Settings
    target[day] = irdstream.Stream2D(
        "targets_" + str(day),
        datadir[day],
        anadir,
        fitsid=fitsid_target[day],
        band=band,
    )
    target[day].info = True  # show detailed info
    target[day].trace = trace_mmf
    # removes noise pattern (makes _cp fits files)
    target[day].clean_pattern(
        trace_mask=trace_mask, extin="", extout="_cp", hotpix_mask=hotpix_mask
    )
    ## Flat fielding
    target[day].apext_flatfield(df_flatn, hotpix_mask=hotpix_mask)
    target[day].dispcor(master_path=thar[day].anadir, extin="_flnhp")

# Blaze function
flat.apext_flatfield(df_flatn,hotpix_mask=hotpix_mask)
flat.dispcor(master_path=thar["day1"].anadir)

# Normalizes the target spectrum
for day in dayarr:
    target[day].normalize1D(master_path=flat.anadir,readout_noise_mode=readout_noise_mode)
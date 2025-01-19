# uses pyird v1.1, Hajime Kawahara

import pathlib

# data directories definition
basedir = pathlib.Path("~/subaru/202501").expanduser()

datadir_flat = basedir / "data/20250114/"
datadir_dark = {}
datadir_dark["h"] = basedir / "data/Kawahara20250113/dark/H-band"
datadir_dark["yj"] = basedir / "data/Kawahara20250113/dark/YJ-band"


dayarr = ["day1", "day2", "day3"]
datadir = {}
datadir["day1"] = basedir / "data/20250114/"
datadir["day2"] = basedir / "data/20250115/"
datadir["day3"] = basedir / "data/20250116/"

anadir = basedir / "anaird2501/reduction/"

band = "h"  #'h' or 'y'
mmf = "mmf2"  #'mmf1' (comb fiber) or 'mmf2' (star fiber)
readout_noise_mode = "default"

# file numbers of fits files (last five digits)
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

# aperture extraction
from pyird.utils import irdstream

flat = irdstream.Stream2D("flat", datadir_flat, anadir)
flat.fitsid = fitsid_flat
flat.band = band

# aperture extraction
if band == "h" and flat.fitsid[0] % 2 == 0:
    flat.fitsid_increment()
    trace_mmf = flat.aptrace(cutrow=1500, nap=21)
elif band == "y":
    trace_mmf = flat.aptrace(cutrow=1000, nap=51)

# trace mask
trace_mask = trace_mmf.mask()

from pyird.image.bias import bias_subtract_image
from pyird.image.hotpix import identify_hotpix_sigclip

## DARK
# Settings
if band == "h":
    rawtag = "IRDAD000"
elif band == "y":
    rawtag = "IRDBD000"
dark = irdstream.Stream2D(
    "dark", datadir_dark[band], anadir, fitsid=fitsid_dark, rawtag=rawtag
)
if band == "h" and dark.fitsid[0] % 2 == 0:
    dark.fitsid_increment()
median_image = dark.immedian()
im_subbias = bias_subtract_image(median_image)
hotpix_mask = identify_hotpix_sigclip(im_subbias)

# ThAr day1-day3
thar = {}
for day in dayarr:
    thar[day] = irdstream.Stream2D(
        "thar_" + str(day),
        datadir[day],
        anadir,
        fitsid=fitsid_thar[day],
    )
    thar[day].trace = trace_mmf
    thar[day].clean_pattern(
        trace_mask=trace_mask, extin="", extout="_cp", hotpix_mask=hotpix_mask
    )
    thar[day].calibrate_wavelength()

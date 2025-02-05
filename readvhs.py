import numpy as np
import pandas as pd
import matplotlib.pyplot as plt



band = "h"
iband = {"h":1, "y":0}
i = iband[band] # h=1, y=0 

bkg2 = [76204+i, 76208+i]
target2 = [76206+i, 76210+i]
bkg3 = list(range(76248+i, 76268+i, 4))
target3 = list(range(76250+i, 76268+i, 4))

bkg = bkg2 + bkg3
target = target2 + target3
#bkg = bkg2
#target = target2
print(bkg, target)

#JWST
path = "../JWST_VHS1256b_Reduction/reduced_spectra/VHS1256b_V2_accepted.txt"
jwst = pd.read_csv(path, delimiter=",", comment="#", names=("wav", "flux", "error", "A"))
#plt.plot(jwst["wav"], jwst["flux"])
#plt.show()
#exit()

def read_wdat(tag, head="ncw"):
    #head  = "nw", "w"
    filename= "reduction/"+ str(head) + str(tag) + "_mmf12.dat"
    
    if head == "nw":
        dat = pd.read_csv(filename, sep=" ", names=("wavelength", "order", "flux", "A", "B"))
    elif head=="ncw":
        dat = pd.read_csv(filename, sep=" ", names=("wavelength", "flux", "A", "B"))
    elif head == "w":
        dat = pd.read_csv(filename, sep=" ", names=("wavelength", "order", "flux"))
    
    return dat

def stack_flux(fitsidset): 
    for i, tag in enumerate(fitsidset):
        dat = read_wdat(tag)
        if i==0:
            flux = dat["flux"]
        else:
            flux += dat["flux"]
    return np.array(dat["wavelength"]), np.array(flux)

def bindata(data, bin_size=100):
    padded_data = np.pad(data, (0, bin_size - len(data) % bin_size), mode='constant',constant_values=np.nan)
    binned_means = np.nanmedian(padded_data.reshape(-1, bin_size), axis=1)
    return binned_means

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    #dat = read_wdat(76249)
    #plt.plot(dat["wavelength"], dat["flux"])
    #plt.show()

    #blaze
    dat = read_wdat("blaze_"+band, head="w")
    blaze = dat["flux"]
    wb = dat["wavelength"]
    
    
    w, fbkg = stack_flux(bkg)
    w, ftarget = stack_flux(target)
    w0 = w[0]
    w1 = w[-1]

    #diff
    fdiff = ftarget - fbkg    

    #binning
    #binning = True
    binning = False    
    bin_size = {"h":20,"y":300}
    if binning:
        w = bindata(w,bin_size=bin_size[band])
        fbkg = bindata(fbkg,bin_size=bin_size[band])
        ftarget = bindata(ftarget,bin_size=bin_size[band])
        fdiff = bindata(fdiff,bin_size=bin_size[band])
        blaze = bindata(blaze,bin_size=bin_size[band])
        wb = bindata(wb,bin_size=bin_size[band])
    
    medblaze = np.median(blaze)
    

    fig = plt.figure(figsize=(10,15))
    ax = fig.add_subplot(311)
    ax.plot(w, fbkg*medblaze, alpha=0.5, label="offset")
    ax.plot(w, ftarget*medblaze, alpha=0.5, label="target")
    ax.set_ylim(-10, 300)
    ax.set_xlim(w0,w1)
    plt.legend()
    ax = fig.add_subplot(312)
    #ax.plot(w, (ftarget - fbkg)/blaze, ".", alpha=0.5, color="C2", label="difference")
    #ax.plot(w, (ftarget - fbkg)*medblaze, ".", alpha=0.9, color="C2", label="bin-diff")
    ax.plot(w, fdiff*medblaze, ".", alpha=0.5, color="C3", label="diff-bin")
    if band == "h":
        plt.plot(jwst["wav"]*1000, jwst["wav"]*jwst["flux"]*0.9*1.e17, color="cyan",alpha=0.5, label="JWST")
        plt.plot(jwst["wav"]*1000, jwst["wav"]*jwst["flux"]*0.9*1.e17 -25.0, color="gray",alpha=0.5, label="JWST - offset")
        ax.set_ylim(-3, 150)
    else:
        plt.plot(jwst["wav"]*1000, jwst["wav"]*jwst["flux"]*0.22*1.e17, color="cyan",alpha=0.5, label="JWST")
        plt.plot(jwst["wav"]*1000, jwst["wav"]*jwst["flux"]*0.22*1.e17 -6.0, color="gray",alpha=0.5, label="JWST - offset")
        ax.set_ylim(-3, 30)
    plt.axhline(0.0, color="black")
    ax.set_xlim(w0,w1)
    plt.legend()
    ax = fig.add_subplot(313)
    ax.plot(wb, blaze/medblaze, alpha=0.5, color="C2", label="blaze")
    ax.set_ylim(-0.1, 3)
    ax.set_xlim(w0,w1)
    ax.set_xlabel("wavelength [nm]")
    plt.legend()
    
    plt.show()
        
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt



band = "h"
iband = {"h":1, "y":0}
i = iband[band] # h=1, y=0 

target2 = list(range(76192+i, 76198+i, 2)) 
target3 = list(range(76240+i, 76248+i, 2)) 

#target = target2


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
    
    
    w, ftarget2 = stack_flux(target2)
    w, ftarget3 = stack_flux(target3)
    
    w0 = w[0]
    w1 = w[-1]

    
    #binning
    #binning = True
    binning = False    
    bin_size = {"h":20,"y":300}
    if binning:
        w = bindata(w,bin_size=bin_size[band])
        ftarget2 = bindata(ftarget2,bin_size=bin_size[band])
        ftarget3 = bindata(ftarget3,bin_size=bin_size[band])
        blaze = bindata(blaze,bin_size=bin_size[band])
        wb = bindata(wb,bin_size=bin_size[band])
    
    medblaze = np.median(blaze)
    

    fig = plt.figure(figsize=(10,5))
    ax = fig.add_subplot(111)
    ax.plot(w, ftarget2*medblaze, alpha=0.5, label="target")
    ax.plot(w, ftarget3*medblaze, alpha=0.5, label="target")
    ax.set_ylim(-10, 1000)
    ax.set_xlim(w0,w1)
    ax.set_xlabel("wavelength [nm]")
    plt.legend()
    
    plt.show()
        
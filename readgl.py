import numpy as np
import pandas as pd
import matplotlib.pyplot as plt



band = "h"
iband = {"h":1, "y":0}
i = iband[band] # h=1, y=0 

target1 = [76014+i, 76018+i, 76020+i]
target2 = list(range(76192+i, 76198+i, 2)) 
target3 = list(range(76240+i, 76248+i, 2)) 

#target = target2


def read_wdat(tag, pi, head="ncw"):
    #head  = "nw", "w"
    filename= "reduction_"+pi+"/"+ str(head) + str(tag) + "_mmf12.dat"
    
    if head == "nw":
        dat = pd.read_csv(filename, sep=" ", names=("wavelength", "order", "flux", "A", "B"))
    elif head=="ncw":
        dat = pd.read_csv(filename, sep=" ", names=("wavelength", "flux", "A", "B"))
    elif head == "w":
        dat = pd.read_csv(filename, sep=" ", names=("wavelength", "order", "flux"))
    
    return dat

def stack_flux(fitsidset, pi): 
    for i, tag in enumerate(fitsidset):
        dat = read_wdat(tag, pi)
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
    dat = read_wdat("blaze_"+band, "yk", head="w")
    blaze_yk = dat["flux"]
    wb_yk = dat["wavelength"]
    dat = read_wdat("blaze_"+band, "hk", head="w")
    blaze_hk = dat["flux"]
    wb_hk = dat["wavelength"]
    
    w_yk, ftarget1 = stack_flux(target1, "yk")
    w_hk, ftarget2 = stack_flux(target2, "hk")
    w_hk, ftarget3 = stack_flux(target3, "hk")
    
    #binning
    #binning = True
    binning = False    
    bin_size = {"h":20,"y":300}
    if binning:
        w_yk = bindata(w_yk,bin_size=bin_size[band])
        w_hk = bindata(w_hk,bin_size=bin_size[band])
        ftarget1 = bindata(ftarget1,bin_size=bin_size[band])
        ftarget2 = bindata(ftarget2,bin_size=bin_size[band])
        ftarget3 = bindata(ftarget3,bin_size=bin_size[band])
        blaze_yk = bindata(blaze_yk,bin_size=bin_size[band])
        blaze_hk = bindata(blaze_hk,bin_size=bin_size[band])
        wb_yk = bindata(wb_yk,bin_size=bin_size[band])
        wb_hk = bindata(wb_hk,bin_size=bin_size[band])
    
    medblaze_yk = np.median(blaze_yk)
    medblaze_hk = np.median(blaze_hk)
    

    w0 = w_hk[0]
    w1 = w_hk[-1]

    fig = plt.figure(figsize=(10,5))
    ax = fig.add_subplot(111)
    ax.plot(w_yk, ftarget1*medblaze_yk, alpha=0.5, label="YK")
    ax.plot(w_hk, ftarget2*medblaze_hk, alpha=0.5, label="HK day2")
    ax.plot(w_hk, ftarget3*medblaze_hk, alpha=0.5, label="HK day3")
    ax.set_ylim(-10, 1000)
    ax.set_xlim(w0,w1)
    ax.set_xlabel("wavelength [nm]")
    plt.legend()
    
    plt.show()
        
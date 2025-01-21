import numpy as np
import pandas as pd

band = "y"
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

def read_wdat(tag, head="w"):
    #head  = "nw", "w"
    filename= "reduction/"+ str(head) + str(tag) + "_mmf12.dat"
    
    if head == "nw":
        dat = pd.read_csv(filename, sep=" ", names=("wavelength", "order", "A", "flux", "B"))
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

def bindata(data, bin_size=30):
    padded_data = np.pad(data, (0, bin_size - len(data) % bin_size), mode='constant')
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
    
    w, fbkg = stack_flux(bkg)
    w, ftarget = stack_flux(target)
    w0 = w[0]
    w1 = w[-1]

    binning = True
    if binning:
        w = bindata(w)
        fbkg = bindata(fbkg)
        ftarget = bindata(ftarget)
        blaze = bindata(blaze)
    
    blaze = blaze/np.median(blaze)

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(311)
    ax.plot(w, fbkg, alpha=0.5, label="offset")
    ax.plot(w, ftarget, alpha=0.5, label="target")
    ax.set_ylim(-10, 300)
    ax.set_xlim(w0,w1)
    plt.legend()
    ax = fig.add_subplot(312)
    ax.plot(w, (ftarget - fbkg)/blaze, ".", alpha=0.5, color="C2", label="difference")
    ax.set_ylim(-10, 200)
    ax.set_xlim(w0,w1)
    plt.legend()
    ax = fig.add_subplot(313)
    ax.plot(w, blaze, alpha=0.5, color="C2", label="blaze")
    ax.set_ylim(-0.1, 2)
    ax.set_xlim(w0,w1)
    ax.set_xlabel("wavelength [nm]")
    plt.legend()
    
    plt.show()
        
import numpy as np
import pandas as pd

#h
bkg = list(range(76249, 76269, 4))
target = list(range(76251, 76269, 4))

#y
bkg = list(range(76248, 76268, 4))
target = list(range(76250, 76268, 4))


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

def bindata(data, bin_size=20):
    padded_data = np.pad(data, (0, bin_size - len(data) % bin_size), mode='constant')
    binned_means = np.nanmean(padded_data.reshape(-1, bin_size), axis=1)
    return binned_means

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    #dat = read_wdat(76249)
    #plt.plot(dat["wavelength"], dat["flux"])
    #plt.show()
    w, fbkg = stack_flux(bkg)
    w, ftarget = stack_flux(target)
    w0 = w[0]
    w1 = w[-1]

    w = bindata(w)
    fbkg = bindata(fbkg)
    ftarget = bindata(ftarget)
    
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(211)
    ax.plot(w, fbkg, alpha=0.5, label="offset")
    ax.plot(w, ftarget, alpha=0.5, label="target")
    ax.set_ylim(-10, 200)
    ax.set_xlim(w0,w1)
    plt.legend()
    ax = fig.add_subplot(212)
    ax.plot(w, ftarget - fbkg, alpha=0.5, color="C2", label="difference")
    ax.set_ylim(-10, 200)
    ax.set_xlim(w0,w1)
    ax.set_xlabel("wavelength [nm]")
    plt.legend()
    plt.show()
        
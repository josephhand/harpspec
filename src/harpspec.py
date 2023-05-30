from TheCannon import dataset as CannonDataset
from TheCannon import model

import os
import numpy as np
import astropy.io.fits as pyfits
import astropy.io.ascii as ascii

from TheCannon.apogee import get_pixmask
from tqdm.autonotebook import trange, tqdm

# Helper functions

def _wl_to_idx(wl, wl_arr):
    return int((wl - wl_arr[0]) / (wl_arr[1] - wl_arr[0]))

# Dataset class

class HARPSpecDataset:
    
    def __init__(self, targets, wl, flux, ivar, labels, label_names):
        self.targets = targets
        self.wl = wl
        self.flux = flux
        self.ivar = ivar
        self.labels = labels
        self.label_names = label_names
        
    def has_labels(self):
        return not self.labels is None
    
    def has_label_names(self):
        return not self.label_names is None
    
    def has_unified_wavelengths(self):
        return not hasattr(self.wl[0], "__len__")

def _load_spectrum(file):
    with pyfits.open(file) as fits:
        target = fits[1].header["TITLE"]
        wl = fits[1].data[0][0]
        flux = fits[1].data[0][1]

        scalefactor = fits[0].header["SNR"] / np.nanmedian(np.sqrt(flux))
        snr = scalefactor * np.sqrt(flux.ravel())
        std = flux / snr

        badpix = get_pixmask(flux, std)
        ivar = np.zeros(len(flux))
        ivar[~badpix] = 1.0 / std[~badpix]**2

    return (target, wl, flux, ivar)

def collate(target):
    
    if not os.path.exists(target):
        raise RuntimeError("Target '%s' does not exist." %target)
        
    if os.path.isdir(target):
        files = list(sorted([target + "/" + filename for filename in os.listdir(target)
            if filename.endswith('.fits') ]))
    else:
        if not target.endswith('.fits'):
            raise RuntimeError("Target '%s' is not a directory or a fits file." %target)
        files = [target]
        
    spectra = np.array([ _load_spectrum(file) for file in tqdm(files) ], dtype=object)
    
    targets = np.array(spectra[:,0])
    wl = np.array(spectra[:,1], dtype=object)
    flux = np.array(spectra[:,2], dtype=object)
    ivar = np.array(spectra[:,3], dtype=object)
    
    return HARPSpecDataset(targets, wl, flux, ivar, None, None)

def load_labels(file):
    
    label_data = ascii.read(file)
    headers = label_data.colnames
    labels = np.array([ label_data[header] for header in headers ]).T
    return labels, headers

def match(dataset, labels):
    
    spectra_targets = dataset.targets
    label_targets = labels[:,0]
    twl = np.nonzero(
        [
            len(np.where(np.array(list(map(lambda a: t.startswith(a), label_targets))) == True)[0])
            for t in spectra_targets
        ]
    )[0]
    tls = [
        np.where(np.array(list(map(lambda a: t.startswith(a), label_targets))) == True)[0][0]
        for t in spectra_targets[twl]
    ]
    if dataset.has_unified_wavelengths:
        return HARPSpecDataset(
            dataset.targets[twl],
            dataset.wl,
            dataset.flux[twl],
            dataset.ivar[twl],
            np.array(labels[tls,1:], dtype=float),
            None
        )
    else:
        return HARPSpecDataset(
            dataset.targets[twl],
            dataset.wl[twl],
            dataset.flux[twl],
            dataset.ivar[twl],
            np.array(labels[tls,1:], dtype=float),
            None
        )

def _align_spectrum(wl, flux, ivar, t_flux, lines = (np.array(range(0,18)) * 100 + 4000), width = 30):
    
    wl_ranges = np.array([
        wl[_wl_to_idx(line - width, wl):_wl_to_idx(line + width, wl)]
        for line in lines
    ])
    
    flux_ranges = np.array([
        flux[_wl_to_idx(line - width, wl):_wl_to_idx(line + width, wl)]
        for line in lines
    ])
    t_flux_ranges = np.array([
        t_flux[_wl_to_idx(line - width, wl):_wl_to_idx(line + width, wl)]
        for line in lines
    ])
    
    z = np.median([ 
        (np.correlate(flux_ranges[i] - flux_ranges[i].mean(),
        t_flux_ranges[i] - t_flux_ranges[i].mean(), mode="full").argmax() -
        len(flux_ranges[i])) * 0.01 / lines[i]
        
        for i in range(0, len(lines))
    ])

    new_flux = np.interp(wl * (1 + z), wl, flux, left=0, right=0)
    new_ivar = np.interp(wl * (1 + z), wl, ivar, left=0, right=0)

    return new_flux, new_ivar

def _bin_flux(flux, ivar):
    if np.sum(ivar)==0:
        return np.mean(flux)
    return np.average(flux, weights=ivar)

def _downsample_wl(wl, amount):

    discard = len(wl) % amount
    if discard != 0:
        wl = np.delete(wl, range(-discard - 1, -1))
    wl = wl.reshape(-1, amount)
    wl_b = np.mean(wl, axis=1)
    return wl_b

def _downsample_spectrum(flux, ivar, amount):

    discard = len(flux) % amount
    if discard != 0:
        flux = np.delete(flux, range(-discard - 1, -1))
        ivar = np.delete(ivar, range(-discard - 1, -1))
    ivar = ivar.reshape(-1, amount)
    flux = flux.reshape(-1, amount)
    ivar_b = np.sqrt(np.sum(ivar**2, axis=1))
    flux_b = np.array([_bin_flux(f, w) for f,w in zip(flux, ivar)])
    return (flux_b, ivar_b)


def process(dataset, params):
    
    targets = dataset.targets
    wl = dataset.wl
    flux = dataset.flux
    ivar = dataset.ivar
    labels = dataset.labels
    label_names = dataset.label_names
    
    new_wl = params["wl"]
    
    flux = np.array([ np.interp(new_wl, wl[i], flux[i], left=0, right=0)
        for i in trange(0, len(wl)) ])
    ivar = np.array([ np.interp(new_wl, wl[i], ivar[i], left=0, right=0)
        for i in trange(0, len(wl)) ])
    wl = new_wl
    
    for i in trange(0, len(flux)):
        flux[i], ivar[i] = _align_spectrum(wl, flux[i], ivar[i], params["reference_flux"])

    dwl = _downsample_wl(wl, params["downsample_amount"])
    downsampled = np.array([
        _downsample_spectrum(flux[i], ivar[i], params["downsample_amount"])
        for i in trange(0, len(flux))
    ])
    dflux = downsampled[:,0]
    divar = downsampled[:,1]
    
    ds = CannonDataset.Dataset(
        dwl,
        targets,
        dflux,
        divar,
        labels,
        np.array(['']),
        np.array([[0] * len(dwl)]),
        np.array([[0] * len(dwl)])
    )
    
    ds.ranges = list(np.array(np.array(params["wl_ranges"])/params["downsample_amount"], dtype=int))
    p_flux, p_ivar = ds.continuum_normalize_training_q(q=0.9, delta_lambda=50)
    contmask = ds.make_contmask(p_flux, p_ivar, frac=0.07)
    ds.set_continuum(contmask)
    cont = ds.fit_continuum(3, "sinusoid")
    norm_flux, norm_ivar, _, _ = ds.continuum_normalize(cont)

    dcont_flux = dflux/norm_flux
    dcont_ivar = divar/norm_ivar

    cont_flux = np.array([ np.interp(wl, dwl, dcont_flux[i]) for i in range(0, len(dcont_flux)) ])
    cont_ivar = np.array([ np.interp(wl, dwl, dcont_ivar[i]) for i in range(0, len(dcont_ivar)) ])

    flux = flux/cont_flux
    ivar = ivar/cont_ivar

    ivar[np.isnan(flux)] = 0
    ivar[np.isnan(ivar)] = 0
    flux[np.isnan(flux)] = 0
    
    return HARPSpecDataset(targets, wl, flux, ivar, labels, label_names)

def train(dataset):
    
    ds = CannonDataset.Dataset(
        dataset.wl,
        None, dataset.flux, dataset.ivar, dataset.labels,
        None, dataset.flux, dataset.ivar
    )
    
    md = model.CannonModel(2, useErrors=False)
    md.fit(ds)
    
    return md

def infer(dataset, md):
    
    label_names = dataset.label_names
    
    # Create default label names if none have been assigned yet.
    if label_names is None:
        print('Creating default label names as none have been assigned yet.')
        label_names = np.array([ "Label-%d" %i for i in range(0, len(dataset.labels[0]))])
    
    ds = CannonDataset.Dataset(
        dataset.wl,
        None, dataset.flux, dataset.ivar, None,
        None, dataset.flux, dataset.ivar
    )
    
    md.infer_labels(ds)
    
    return HARPSpecDataset(dataset.targets, dataset.wl, dataset.flux, dataset.ivar, ds.test_label_vals)
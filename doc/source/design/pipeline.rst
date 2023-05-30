Spectral Processing Pipeline
============================

The spectral processing pipeline is the heart of HARPSpec, as it allows The
Cannon to work properly. It is responsible for performing the following steps to
prepare the spectra for training or inference.

#. Creating a unified wavelength array.
#. Aligning spectra to vacuum rest frame.
#. Continuum normalizing the spectra.

These steps and the methods used to complete them are described here.

Creating a Unified Wavelength Array
-----------------------------------

Spectra in HARPSpec are stored as two arrays, one that contains the wavelengths
of each data-point, and another with the spectral intensity of each data-point.
Since The Cannon relies on correlations between identical data-points in each
spectrum to function, is is important that the wavelength arrays for each
spectrum are the same. They must cover the same range of wavelengths with the
same number of data-points spaced in the same way.

Since all spectra used in HARPSpec are obtained from the same source, the HARPS
spectrograph, this is almost the case. However, the processing done by the ESO
on these spectra beforehand create slight variations in the ranges of
wavelengths covered by the spectra.

In order to correct for these variations, the spectra are all resampled to a
unified wavelength array. This array is calculated from the spectra in the
dataset by obtaining the maximum and minimum wavelengths included in any of the
spectra. When resampling, any datapoints created that do not correspond to data
within the original dataset are marked with a inverse variance of 0, indicating
that the datapoint has infinite uncertainty and should have a weight of zero in
future calculations.

Aligning to Vacuum Rest Frame
-----------------------------

As The Cannon is extremely sensitive to alignment between the spectra, it is
important that all spectra are aligned to vacuum rest frame. The spectra
obtained from the ESO were analyzed and found to be shifted slightly reletive to
each other, enough to significantly negatively affect the performance of The
Cannon.

To account for this, the spectra were aligned to vacuum rest frame by first
manually aligning one of the spectra, this provided a "template" that could be
used to guage how misaligned other spectra were.

The remaining spectra were aligned by cross-correlating many small segments from
each individual spectrum with the corresponding segments from the template
spectrum. This cross correlation was used to obtain the amount the segments had
to be shifted relative to each other in order to line up as much as possible. By
averaging the shifts required over a large number of segments, and accurate
measure the the relative readshift between the spectra could be obtained. Since
one of the spectra was known to be in vacuum rest frame, this gives the absolute
redshift of the other spectrum. Knowing the absolute redshift of a spectrum
allows for it to be easily shifted to rest frame. This process was repeated with
all spectra used to ensure all spectra were in rest frame.

Continuum Normalization
-----------------------

The Cannon expects spectra used with it to be continuum-normalized. Because of
this, it is distributed with the tools required to continuum normalize spectra
in a way that is optimal for the library. HARPSpec uses these tools to continuum
normalize spectra as part of the spectral processing pipeline.

Due to the large size of the spectra obtained from HARPS, the spectra are
downsampled before being continuum normalized. This allows for the continuum
normalization to be performed much faster. The resulting continuum normalized
spectra are divided into the original downsampled spectra to yield "continuum"
spectra that contain the continuum fits obtained as part of the continuum
normalization. The continuum spectra are then upsampled and divided into the
original spectra to yield the full-resolution, continuum normalized spectra.

The Cannon
==========

The Cannon is a tool created by Melissa Ness, David W. Hogg, Hans-Walter Rix,
Anna Y. Q. Ho, and Gail Zasowski [NESS2015]_. It is designed to offer an alternative
approach to deriving stellar parameters, such as elemental abundances,  from
stellar spectra that is more efficient than previous means. It accomplishes this
by utilizing a data-driven approach that relies on an existing dataset of
spectra with accurate parameters assigned to them. By analyzing the pattern and
relationships between the different spectral elements and the parameters given,
The Cannon can create a model that is capable of accurately assign parameters to
new spectra that were not in the original dataset.

As this data-driven techniques does not rely on manually identifying and
isolating absorption lines from individual spectra, it can work much more
quickly than other techniques for parameter assignment. Additionally, the model
obtained can be used on a limitless number of spectra, as long as they are
obtained and processed identically to the spectra in the original dataset.

An example of an existing use of this tool can be seen in [HO2016]_.


.. [NESS2015] Ness et al. *The Cannon: A data-driven approach to stellar label
   determination*. 2015. https://doi.org/10.48550/arXiv.1501.07604

.. [HO2016] Ho et al. *Label Transfer from APOGEE to LAMOST: Precise Stellar
   Parameters for 450,000 LAMOST Giants*. 2016.
   https://doi.org/10.48550/arXiv.1602.00303

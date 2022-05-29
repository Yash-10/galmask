.. galmask documentation master file, created by
   sphinx-quickstart on Tue May 24 11:43:52 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

galmask: An unsupervised galaxy masking approach
================================================

**galmask** is an open-source package written in Python that provides a simple way to remove unwanted
background source detections from galaxy images. It builds on top of `astropy` and `photutils`
astronomical Python libraries and the `opencv` and `skimage` image processing libraries.

`galmask` works as follows: Given a galaxy image, and optionally an estimate of the segmentation map,
it gets rid of background detections around the galaxy which typically affect downstream analysis concerned
with the morphology of galaxies. To achieve this, it efficiently uses the concepts of deblending and
optionally, connected-component analysis.

Installation
============

Requirements
############

- `astropy` for handling FITS I/O and general-purpose astronomical routines.
- `photutils` for photometry purposes and deblending detected sources.
- `opencv-python` for connected-component analysis.
- `skimage` for general image processing functionalities.

Via `pip`
#########

`galmask` can be installed from PyPI via `pip` by running::

   pip install galmask

Alternative method
##################

`galmask` can also be installed by cloning the repository and doing a pip install in the project directory::

   git clone https://github.com/Yash-10/galmask
   cd galmask
   pip install .

Example usage
===============
::

   from astropy.io import fits
   from galmask.galmask import galmask

   image = fits.getdata('example/gal.fits')
   seg_image = fits.getdata('example/gal_segment.fits')

   # Set some parameter values
   npixels, nlevels, nsigma, contrast, min_distance, num_peaks, num_peaks_per_label = 5, 32, 3., 0.001, 1, 9, 3

   connectivity = 4  # Can be 4 or 8.
   mode = "1"  # Can be 0, 1, or 2.
   deblend = True  # We want to deblend sources.
   kernel = None  # Use a 2D Gaussian kernel with FWHM = 3 defined internally.

   # Run galmask
   final_seg_image, final_image = galmask(
      image, npixels, nlevels, nsigma, contrast, min_distance, num_peaks, num_peaks_per_label,
      connectivity=connectivity, kernel=kernel, seg_image=seg_image
   )

It returns the final segmentation map along with the final galaxy image which can now be used in downstream analyses.


Running tests and building the documentation
============================================

To run tests locally, you would need to install `pytest https://docs.pytest.org/`__. Once done, you can
navigate to the `tests/` directory and run, for example::

   pytest test_galmask.py

If you would like to build the documentation locally, you can do::

    cd docs/
    make html
    python -m http.server

You can open http://0.0.0.0:8000/ in your browser.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

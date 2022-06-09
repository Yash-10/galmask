.. galmask documentation master file, created by
   sphinx-quickstart on Tue May 24 11:43:52 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

galmask: An unsupervised galaxy masking package
===============================================

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
   from astropy.visualization import AsinhStretch, ImageNormalize, ZScaleInterval, LogStretch

   import matplotlib.pyplot as plt
   from mpl_toolkits.axes_grid1 import make_axes_locatable

   # Import galmask
   from galmask.galmask import galmask

   def axes_colorbar(ax):
      divider = make_axes_locatable(ax)
      cax = divider.append_axes('bottom', size='5%', pad=0.3)
      return cax

   filepath = 'example/gal2_R.fits'
   image = fits.getdata(filepath)
   npixels, nlevels, nsigma, contrast, min_distance, num_peaks, num_peaks_per_label, connectivity, remove_local_max = 5, 32, 2., 0.15, 1, 10, 3, 4, True  # Parameters for galmask
   seg_image = None  # No segmentation map example
   orig_segmap = fits.getdata('example/gal2_orig_segmap_R.fits')

   galmasked, galsegmap = galmask(
      image, npixels, nlevels, nsigma, contrast, min_distance, num_peaks, num_peaks_per_label,
      connectivity=4, kernel=fits.getdata('kernel.fits'), seg_image=seg_image, mode="1",
      remove_local_max=True, deblend=True
   )

   # Plotting result.
   fig, ax = plt.subplots(1, 4, figsize=(24, 6))

   # For keeping original and final images on same scale.
   vmin = min(image.min(), galmasked.min())
   vmax = max(image.max(), galmasked.max())

   # fig.suptitle(filepath)
   norm1 = ImageNormalize(image, vmin=vmin, vmax=vmax, interval=ZScaleInterval(), stretch=LogStretch())
   im0 = ax[0].imshow(image, norm=norm1, origin='lower', cmap='gray')
   ax[0].set_title("Original image")
   cax0 = axes_colorbar(ax[0])
   fig.colorbar(im0, cax=cax0, orientation='horizontal')

   im1 = ax[1].imshow(orig_segmap, origin='lower')
   ax[1].set_title("Original segmentation map (photutils)")
   cax1 = axes_colorbar(ax[1])
   fig.colorbar(im1, cax=cax1, orientation='horizontal')

   im2 = ax[2].imshow(galsegmap, origin='lower', cmap='gray')
   ax[2].set_title("Final segmentation map (galmask)")
   cax2 = axes_colorbar(ax[2])
   fig.colorbar(im2, cax=cax2, orientation='horizontal')

   norm2 = ImageNormalize(galmasked, vmin=vmin, vmax=vmax, interval=ZScaleInterval(), stretch=LogStretch())
   im3 = ax[3].imshow(galmasked, norm=norm2, origin='lower', cmap='gray')
   ax[3].set_title("Final image (galmask)")
   cax3 = axes_colorbar(ax[3])
   fig.colorbar(im3, cax=cax3, orientation='horizontal')

   plt.show()

Output:

.. image:: ../example/galmask_example2.png
  :width: 1000
  :alt: galmask example usage

It returns the final segmentation map (column 3) along with the final galaxy image (last column) which can now be used in downstream analyses.


.. note::
   It is important to note that ``galmask`` returns the final image in which the background pixels are set to zero.
   However, you could replace all such pixels with a background estimated from the original input image. 

General tips
============

Note that most of the parameters like ``npixels``, ``nlevels``, etc. are passed directly to downstream methods:

- ``npixels`` is passed to the ``detect_sources`` method from ``photutils``.
- ``npixels``, ``nlevels``, and ``contrast`` are passed to the ``deblend_sources`` method from ``photutils``.
- ``min_distance``, ``num_peaks``, and ``num_peaks_per_label`` are passed to the ``peak_local_max`` function from ``skimage``.
- ``connectivity`` is used for the connected-component analysis from ``opencv-python``.

Hence, a better understanding and usage of these parameters can be seen from their respective documentation.

Here are some empirical notes and tips:

#. If there are nearby sources in your image, you might want to set ``deblend = True``.
#. Using 8-connectivity tends to maximizes connection of objects together. So use 4-connectivity if you do not want to maximize the connection.
#. For better performance, it might be helpful to input a custom ``kernel`` and ``seg_image`` since it alleviates some internal calculations.
#. If unsure, set ``remove_local_max = True``.
#. The ``mode`` argument is an important one since the results significantly depend on this value. It might happen that ``mode = 1`` works well for one image but not for the other, for example. **Although mode = 1 is the default, you might want to experiment with the other options to choose the best option for your image. So, currently, you might need to try all the three possible modes**. We empirically find atleast one mode out of the possible three modes to work for any given image.
#. The results do depend on the segmentation map, if any, input to galmask since it used as a basis for further cleaning of the map. So please ensure that your segmentation map is plausible.
#. If you want to input a custom segmentation map, we would recommend using the `NoiseChisel <https://www.gnu.org/software/gnuastro/manual/html_node/NoiseChisel.html>`__ program that does a great job to detect nebulous objects like irregular galaxies and helps particularly in detecting fainter outskirts of a galaxy.

Running tests and building the documentation
============================================

To run tests locally, you would need to install `pytest <https://docs.pytest.org/>`__. Once done, you can
navigate to the `tests/` directory and run, for example::

   pytest test_galmask.py

and it should run without any failures!

If you would like to build the documentation locally, you can do::

    cd docs/
    make html
    python -m http.server

You can then open the url http://0.0.0.0:8000/ in your browser.

References and Acknowledgments
==============================

#. Astropy Collaboration, Robitaille, T. P., Tollerud, E. J., et al. 2013, A&A, 558, A33, doi: 10.1051/0004-6361/201322068
#. Astropy Collaboration, Price-Whelan, A. M., Sip˝ocz, B. M., et al. 2018, AJ, 156, 123, doi: 10.3847/1538-3881/aabc4f
#. Bradley, L., Sipocz, B., Robitaille, T., et al. 2016, Photutils: Photometry tools, Astrophysics Source Code Library, record ascl:1609.011. http://ascl.net/1609.011
#. Stéfan van der Walt, Johannes L. Schönberger, Juan Nunez-Iglesias, François Boulogne, Joshua D. Warner, Neil Yager, Emmanuelle Gouillart, Tony Yu and the scikit-image contributors. scikit-image: Image processing in Python. PeerJ 2:e453 (2014) https://doi.org/10.7717/peerj.453
#. Bradski, G., 2000. The OpenCV Library. Dr. Dobb&#x27;s Journal of Software Tools.

- This research made use of `Astropy <https://www.astropy.org>`__, a community-developed core Python package for Astronomy (Robitaille et al., 2013, Price-Whelan et al., 2018)
- This research made use of `Photutils <https://photutils.readthedocs.io/>`__, an Astropy package for detection and photometry of astronomical sources (Bradley et al. 2022).

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

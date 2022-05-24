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
it gets rid of background detections around the galaxy which typically affect the analysis of galaxies.
To achieve this, it efficiently uses the concepts of deblending and connected-component analysis.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

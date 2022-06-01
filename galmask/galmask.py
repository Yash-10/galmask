import cv2
import numpy as np
import warnings

from skimage.feature import peak_local_max

from astropy.io import fits
from astropy.convolution import convolve, Gaussian2DKernel
from astropy.stats import sigma_clipped_stats, gaussian_fwhm_to_sigma

from photutils.background import MedianBackground, Background2D
# from photutils.detection import find_peaks
from photutils.datasets import apply_poisson_noise
from photutils.segmentation import deblend_sources, detect_sources, detect_threshold

from galmask.utils import find_farthest_label, find_closest_label, getLargestCC


def galmask(
    image, npixels, nlevels, nsigma, contrast, min_distance, num_peaks, num_peaks_per_label,
    connectivity=4, kernel=None, seg_image=None, mode="1", remove_local_max=True, deblend=True
):
    """Removes background source detections from input galaxy image.

    :param image: Galaxy image.
    :type image: numpy.ndarray
    :param npixels: The no. of connected pixels that an object must have to be detected.
    :type npixels: int
    :param nlevels: No. of multi-thresholding levels to be used for deblending.
    :type nlevels: int
    :param nsigma: No. of standard deviations per pixel above the background to be considered as a part of source.
    :type nsigma: float
    :param contrast: Controls the level of deblending.
    :type contrast: float
    :param min_distance: The minimum distance between distinct local peaks.
    :type min_distance: int
    :param num_peaks: Maximum no. of peaks in the image.
    :type num_peaks: int
    :param num_peaks_per_label: Maximum no. of peaks per label of the segmentation map.
    :type num_peaks_per_label: int
    :param connectivity: Either 4 or 8, defaults to 4.
    :type connectivity: int
    :param kernel: Kernel array to use for convolution.
    :type kernel: numpy.ndarray, optional
    :param seg_image: Segmentation map.
    :type seg_image: numpy.ndarray, optional
    :param mode: If "1", then performs connected component analysis else not, defaults to "1".
    :type mode: str, optional
    :param remove_local_max: Whether to remove labels corresponding to peak local maximas far away from the center. If unsure, keep the default, defaults to `True`.
    :type remove_local_max: bool, optional
    :param deblend: Whether to deblend sources in the image. Set to True if there are nearby/overlapping sources in the image, defaults to `True`.
    :type deblend: bool, optional

    :return cleaned_seg_img: Cleaned segmentation after removing unwanted source detections.
    :rtype: numpy.ndarray

    The method assumes the image is more or less centered on the galaxy image. If it is not, one needs to shift the
    image appropriately.

    """
    _img_shape = image.shape

    # Convolve input image with a 2D kernel.
    if kernel is None:  # Create a Gaussian kernel with FWHM = 3.
        sigma = 3.0 * gaussian_fwhm_to_sigma
        kernel = Gaussian2DKernel(sigma, x_size=3, y_size=3)
        kernel.normalize()
        kernel = kernel.array

    if not np.allclose(np.sum(kernel), 1.0):
        warnings.warn("Kernel is not normalized.")
    if np.isclose(np.sum(kernel), 0.0):
        raise ValueError("Kernel sum is close to zero. Cannot use it for convolution.")

    bkg_level = MedianBackground().calc_background(image)
    image_bkg_subtracted = image - bkg_level
    convolved_data = convolve(image_bkg_subtracted, kernel, normalize_kernel=True)

    if seg_image is None:
        threshold = detect_threshold(image_bkg_subtracted, nsigma=nsigma, background=0.0)
        # Since threshold includes background level, we do not subtract background from data that is input to detect_sources.
        objects = detect_sources(convolved_data, threshold, npixels=npixels)
        if objects is None:
            raise ValueError("No source detection found in the image!")
        objects = objects.data
    else:
        objects = seg_image.copy()
        objects = objects.astype('uint8')

    if deblend:
        segm_deblend = deblend_sources(convolved_data, objects, npixels=npixels, nlevels=nlevels, contrast=contrast).data
    else:
        segm_deblend = objects

    if remove_local_max:
        local_max = peak_local_max(
            convolved_data, min_distance=min_distance, num_peaks=num_peaks, num_peaks_per_label=num_peaks_per_label, labels=segm_deblend
        )
        index = find_farthest_label(local_max, _img_shape[0]/2, _img_shape[1]/2)
        val = segm_deblend[local_max[index][0], local_max[index][1]]
        segm_deblend[segm_deblend==val] = 0

    segm_deblend_copy = segm_deblend.copy()

    if mode == "0":  # Seems to be better if many unwanted small detections around central galaxy. eg: Antila images of S-PLUS dataset.
        largestCC = getLargestCC(objects).astype(float)
        x = largestCC.copy()
    elif mode == "1":  # Seems to work if not too many detections around central galaxy. eg: OMEGA dataset.
        segm_deblend_copy = segm_deblend_copy.astype('uint8')
        # Below line has issues with opencv-python-4.5.5.64, so to fix, downgrade the version.
        nb_components, objects_connected, stats, centroids = cv2.connectedComponentsWithStats(segm_deblend_copy, connectivity=connectivity)  # We want to remove all detections far apart from the central galaxy.
        max_label, max_size = max([(i, stats[i, cv2.CC_STAT_AREA]) for i in range(1, nb_components)], key=lambda x: x[1])
        # The below lines of code are to ensure that if the central source (which is of concern) is not of maximum area, then we should
        # not remove it, and instead select the center source by giving it more priority than area-wise selection. If indeed the central
        # source is of the greatest area, then we can just select it.
        closest_to_center_label = find_closest_label(centroids[1:, :], _img_shape[0]/2, _img_shape[1]/2)  # The first row in `centroids` corresponds to the whole image which we do not want. So consider all rows except the first.
        if closest_to_center_label == max_label:
            x = (objects_connected == max_label).astype(float)
        else:
            x = (objects_connected == closest_to_center_label).astype(float)
    elif mode == "2":
        largestCC = getLargestCC(segm_deblend_copy).astype(float)
        x = largestCC.copy()

    galmasked = np.multiply(x, image)

    return galmasked, x

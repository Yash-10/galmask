import cv2
import numpy as np

from skimage.feature import peak_local_max

from astropy.io import fits
from astropy.convolution import convolve
from astropy.stats import sigma_clipped_stats, gaussian_fwhm_to_sigma

from photutils.background import MedianBackground
# from photutils.detection import find_peaks
from photutils.segmentation import deblend_sources, detect_sources, detect_threshold

from galmask.utils import find_farthest_label, find_closest_label, getLargestCC


def clean(
    image, npixels, nlevels, nsigma, contrast, min_distance, num_peaks, num_peaks_per_label,
    connectivity=4, kernel=None, seg_image=None, mode="1", remove_local_max=True, deblend_sources=True
):
    """Removes background source detections from input galaxy image.

    Parameters
    ----------
    image: numpy.ndarray
        Galaxy image.
    npixels: int
        The no. of connected pixels that an object must have to be detected.
    nlevels: int
        No. of multi-thresholding levels to be used for deblending.
    nsigma: float
        No. of standard deviations per pixel above the background to be considered as a part of source.
    contrast: float
        Controls the level of deblending.
    min_distance: int
        The minimum distance between distinct local peaks.
    num_peaks: int
        Maximum no. of peaks in the image.
    num_peaks_per_label: int
        Maximum no. of peaks per label of the segmentation map.
    connectivity: int, optional
        Either 4 or 8, defaults to 4.
    kernel: numpy.ndarray, optional
        Kernel array to use for convolution.
    seg_image: numpy.ndarray, optional.
        Segmentation map.
    mode: str, optional
        If "1", then performs connected component analysis else not.
    remove_local_max: bool, optional
        Whether to remove labels corresponding to peak local maximas far away from the center.
        If unsure, keep the default, i.e. True.
    deblend_sources: bool, optional
        Whether to deblend sources in the image.
        Set to True if there are nearby/overlapping sources in the image.

    Return
    ------
    cleaned_seg_img: numpy.ndarray
        Cleaned segmentation after removing unwanted source detections.

    Notes
    -----
    The method assumes the image is more or less centered on the galaxy image. If it is not, one needs to shift the
    image appropriately.

    """
    _img_shape = image.shape

    # Convolve input image with a 2D kernel.
    if kernel is None:  # Create a Gaussian kernel with FWHM = 3.
        sigma = 3.0 * gaussian_fwhm_to_sigma
        kernel = Gaussian2DKernel(sigma, x_size=3, y_size=3)

    if not np.allclose(np.sum(kernel), 1.0):
        warnings.warn("Kernel is not normalized.")
    if np.isclose(np.sum(kernel), 0.0):
        raise ValueError("Kernel sum is close to zero. Cannot use it for convolution.")

    convolved_data = convolve(gal_data, kernel, normalize_kernel=True)

    if seg_image is None:
        bkg_level = MedianBackground().calc_background(image)
        threshold = detect_threshold(image - bkg_level, nsigma=nsigma)
        objects = detect_sources(convolved_data, threshold, npixels=npixels).data
    else:
        objects = seg_image.copy()
        objects = objects.astype('uint8')

    if deblend_sources:
        segm_deblend = deblend_sources(convolved_data, objects, npixels=npixels, nlevels=nlevels, contrast=contrast).data
    else:
        segm_deblend = objects

    if remove_local_max:
        local_max = peak_local_max(
            convolved_data, min_distance=min_distance, num_peaks=num_peaks, num_peaks_per_label=num_peaks_per_label, labels=segm_deblend.data
        )
        index = find_farthest_label(local_max, _img_shape/2, _img_shape/2)
        val = segm_deblend[local_max[index][0], local_max[index][1]]
        segm_deblend[segm_deblend==val] = 0

    segm_deblend_copy = segm_deblend.copy()

    if mode == "0":  # Seems to be better if many unwanted small detections around central galaxy. eg: Antila images of S-PLUS dataset.
        largestCC = getLargestCC(objects).astype(int)
        x = largestCC.copy()
    elif mode == "1":  # Seems to work if not too many detections around central galaxy. eg: OMEGA dataset.
        segm_deblend_copy = segm_deblend_copy.astype('uint8')
        nb_components, objects_connected, stats, centroids = cv2.connectedComponentsWithStats(segm_deblend_copy, connectivity=connectivity)  # We want to remove all detections far apart from the central galaxy.
        max_label, max_size = max([(i, stats[i, cv2.CC_STAT_AREA]) for i in range(1, nb_components)], key=lambda x: x[1])
        # The below lines of code are to ensure that if the central source (which is of concern) is not of maximum area, then we should
        # not remove it, and instead select the center source by giving it more priority than area-wise selection. If indeed the central
        # source is of the greatest area, then we can just select it.
        closest_to_center_label = find_closest_label(centroids[1:, :], _img_shape/2, _img_shape/2)  # The first row in `centroids` corresponds to the whole image which we do not want. So consider all rows except the first.
        if closest_to_center_label == max_label:
            x = (objects_connected == max_label).astype(int)
        else:
            x = (objects_connected == closest_to_center_label).astype(int)

    return x

import cv2
import numpy as np

from astropy.io import fits
from astropy.convolution import convolve
from astropy.stats import sigma_clipped_stats

from skimage.feature import peak_local_max
from skimage.measure import label

from photutils.background import MedianBackground, Background2D
from photutils.detection import find_peaks
from photutils.segmentation import deblend_sources, detect_sources, detect_threshold


def find_farthest_label(coords, refx, refy):  # TODO: This function is slow and inefficient -- rewrite using standard libraries.
    max_dist = -np.Inf
    max_index = -99
    for i in range(coords.shape[0]):
        dist = abs(coords[i][0] - refx) + abs(coords[i][1] - refy)
        if dist > max_dist:
            max_dist = dist
            max_index = i

    return max_index

def find_closest_label(coords, refx, refy):
    min_dist = np.Inf
    min_index = 99999
    for i in range(coords.shape[0]):
        dist = abs(coords[i][0] - refy) + abs(coords[i][1] - refx)
        if dist < min_dist:
            min_dist = dist
            min_index = i

    return min_index + 1

def clean(image, npixels, nlevels, contrast, min_distance, num_peaks, num_peaks_per_label, connectivity, kernel_filename=None, seg_image=None, mode="1", remove_local_max=True):
    """
    Cleans an input galaxy image by removing unwanted detections.
    
    Parameters
    ----------
    
    Return
    ------


    """
    _img_shape = image.shape

    # Convolve input image with a 2D kernel.
    if kernel_filename is None:  # Create a Gaussian kernel with FWHM = 3.
        sigma = 3.0 * gaussian_fwhm_to_sigma
        kernel = Gaussian2DKernel(sigma, x_size=3, y_size=3)
    else:
        kernel = fits.getdata(kernel_filename)

    if not np.allclose(np.sum(kernel), 1.0):
        warnings.warn("Kernel is not normalized.")
    if np.isclose(np.sum(kernel), 0.0):
        raise ValueError("Kernel sum is close to zero. Cannot use it for convolution.")

    convolved_data = convolve(gal_data, kernel, normalize_kernel=True)

    if seg_image is None:
        bkg_level = MedianBackground().calc_background(image)
        threshold = detect_threshold(image - bkg_level, nsigma=2.)
        objects = detect_sources(convolved_data, threshold, npixels=5).data
    else:
        objects = seg_image.copy()
        objects = objects.astype('uint8')

    segm_deblend = deblend_sources(convolved_data, objects, npixels=npixels, nlevels=nlevels, contrast=contrast).data

    if remove_local_max:
        # mean, median, std = sigma_clipped_stats(convolved_data, sigma=3.0)
        # table = find_peaks(
        #     convolved_data, threshold=median+5*std, box_size=5
        # )
        # local_max = np.array(table[['y_peak', 'x_peak']])
        local_max = peak_local_max(
            convolved_data, min_distance=min_distance, num_peaks=num_peaks, num_peaks_per_label=num_peaks_per_label, labels=segm_deblend.data
        )
        index = find_farthest_label(local_max, _img_shape/2, _img_shape/2)
        val = segm_deblend[local_max[index][0], local_max[index][1]]
        segm_deblend[segm_deblend==val] = 0

    segm_deblend_copy = segm_deblend.copy()

    if mode == "0":  # Seems to be better if many unwanted small detections around central galaxy. eg: Antila images of S-PLUS dataset.
        largestCC = getLargestCC(objects).astype(int)
        # deblended_seg = deblend_sources(largestCC * gal_data, largestCC, npixels=npixels, nlevels=nlevels, contrast=0).data
        x = largestCC.copy()
    elif mode == "1":  # Seems to work if not too many detections around central galaxy. eg: OMEGA dataset.
        segm_deblend_copy = segm_deblend_copy.astype('uint8')
        nb_components, objects_connected, stats, centroids = cv2.connectedComponentsWithStats(segm_deblend_copy, connectivity=connectivity)  # We want to remove all detections far apart from the central galaxy.
        max_label, max_size = max([(i, stats[i, cv2.CC_STAT_AREA]) for i in range(1, nb_components)], key=lambda x: x[1])
        # The below lines of code are to ensure that if the central source (which is of concern) is not of maximum area, then we should
        # not remove it, and instead select the center source by giving it more priority than area-wise selection. If indeed the central
        # source is of the greatest area, then we can just select it.
        closest_to_center_label = find_closest_label(centroids[1:, :], 100, 100)  # The first row in `centroids` corresponds to the whole image which we do not want. So consider all rows except the first.
        if closest_to_center_label == max_label:
            x = (objects_connected == max_label).astype(int)
        else:
            x = (objects_connected == closest_to_center_label).astype(int)

    return x

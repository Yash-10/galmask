import cv2
import numpy as np

from astropy.io import fits
from astropy.convolution import convolve
from skimage.feature import peak_local_max
from photutils.segmentation import deblend_sources


def find_farthest_label(coords, refx, refy):
    max_dist = -np.Inf
    max_index = -99
    for i in range(coords.shape[0]):
        dist = abs(coords[i][0] - refx) + abs(coords[i][1] - refy)
        if dist > max_dist:
            max_dist = dist
            max_index = i
    return max_index

def clean(filename, npixels, nlevels, contrast, min_distance, num_peaks, num_peaks_per_label, connectivity):
    hdul = fits.open(filename)
    gal_data = hdul[1].data
    _img_shape = gal_data.shape
    objects = hdul[3].data
    objects = objects.astype('uint8')
    
    kernel = fits.getdata("kernel.fits")
    convolved_data = convolve(gal_data, kernel)  # TODO: Define a gaussian kernel of some width if "kernel.fits" not given.
    segm_deblend = deblend_sources(convolved_data, hdul[3].data, npixels=npixels, nlevels=nlevels, contrast=contrast)

    local_max = peak_local_max(
        convolved_data, min_distance=min_distance, num_peaks=num_peaks, num_peaks_per_label=num_peaks_per_label, labels=segm_deblend.data
    )
    index = find_farthest_label(local_max, _img_shape/2, _img_shape/2)  # TODO: Ideally you want to remove n-1 labels where n is all labels after deblending.
    val = segm_deblend.data[local_max[index][0], local_max[index][1]]
    # print(index)
    # print(local_max)
    segm_deblend.data[segm_deblend.data==val] = 0

    segm_deblend_copy = segm_deblend.data.copy()
    
    segm_deblend_copy = segm_deblend_copy.astype('uint8')
    nb_components, objects_connected, stats, _ = cv2.connectedComponentsWithStats(segm_deblend_copy, connectivity=connectivity)  # We want to remove all detections far apart from the central galaxy.
    max_label, max_size = max([(i, stats[i, cv2.CC_STAT_AREA]) for i in range(1, nb_components)], key=lambda x: x[1])
    x = (objects_connected == max_label).astype(int)
    
    return x

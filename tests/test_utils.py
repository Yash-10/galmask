import os
import pytest
import numpy as np
from astropy.io import fits

from galmask.utils import find_closest_label, find_farthest_label, getLargestCC, getCenterLabelRegion

current_dir = os.path.dirname(os.path.abspath(__file__))

def test_farthest_coordinate():
    coords1 = np.array([
        [50, 50],
        [25, 25],
        [75, 75],
        [90, 90],
        [10, 10]
    ])
    coords2 = np.array([
        [-50, 50],
        [25, 25],
        [75, 75],
        [90, 90],
        [10, 10]
    ])

    assert find_farthest_label(coords1, 100, 100) == 4
    assert find_farthest_label(coords2, 100, 100) == 0

def test_closest_coordinate():
    coords1 = np.array([
        [50, 50],
        [25, 25],
        [90, 90],
        [75, 75],
        [10, 10]
    ])
    coords2 = np.array([
        [50, 50],
        [25, 25],
        [90, -90],
        [75, 75],
        [10, 10]
    ])

    assert find_closest_label(coords1, 100, 100) == 3  # find_closest_label returns index + 1
    assert find_closest_label(coords2, 100, 100) == 4  # find_closest_label returns index + 1

def test_getLargestCC():
    fits_file = os.path.join(current_dir, 'data/test_getLargestCC_seg_map.fits')
    segmap = fits.getdata(fits_file)
    largestCC_segmap = getLargestCC(segmap).astype(int)

    assert len(np.unique(largestCC_segmap)) == 2
    assert 0 in largestCC_segmap and 1 in largestCC_segmap

def test_getCenterLabelRegion_two_labels():
    # Create a case where central object is not of the largest area -> returned object must be central though.
    segmap = np.zeros((50, 50), dtype=int)
    segmap[23:27, 23:27] = 1
    segmap[35:48, 35:48] = 2
    final_segmap = getCenterLabelRegion(segmap)  # Must return the object with label 1 even if it was area-wise smaller since it is the closest to the center.
    xindices, yindices = np.nonzero(final_segmap)

    assert len(np.unique(final_segmap)) == 2

    assert xindices.max() == 26
    assert xindices.min() == 23
    assert yindices.max() == 26
    assert yindices.min() == 23

def test_getCenterLabelRegion_multiple_labels():
    # Create a case where central object is not of the largest area -> returned object must be central though.
    segmap = np.zeros((50, 50), dtype=int)
    segmap[23:27, 23:27] = 1
    segmap[35:48, 35:48] = 2
    segmap[3:18, 3:18] = 3
    segmap[18:24, 18:24] = 4
    final_segmap = getCenterLabelRegion(segmap)  # Must return the object with label 1 even if it was area-wise smaller since it is the closest to the center.
    xindices, yindices = np.nonzero(final_segmap)

    assert len(np.unique(final_segmap)) == 2

    assert xindices.max() == 26
    assert xindices.min() == 23
    assert yindices.max() == 26
    assert yindices.min() == 23

def test_getCenterLabelRegion_segmap():  # This is just an additional test on an actual segmentation map.
    # Create a case where central object is not of the largest area -> returned object must be central though.
    segmap = fits.getdata(
        os.path.join(current_dir, 'data/test_getCenterLabelRegion_segmap.fits')
    )
    final_segmap = getCenterLabelRegion(segmap)
    xindices, yindices = np.nonzero(final_segmap)

    assert len(np.unique(final_segmap)) == 2
    assert xindices.max() > 152
    assert xindices.min() < 212
    assert yindices.max() > 156
    assert yindices.min() < 204

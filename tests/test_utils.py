import pytest
import numpy as np
from astropy.io import fits

from galmask.utils import find_closest_label, find_farthest_label, getLargestCC


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
    segmap = fits.getdata('./data/test_getLargestCC_seg_map.fits')
    largestCC_segmap = getLargestCC(segmap).astype(int)

    assert len(np.unique(largestCC_segmap)) == 2
    assert 0 in largestCC_segmap and 1 in largestCC_segmap

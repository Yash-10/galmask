import pytest
import numpy as np
from astropy.convolution import Gaussian2DKernel

from photutils.datasets import make_100gaussians_image

from galmask.gal_mask import galMask


@pytest.mark.filterwarnings("ignore::UserWarning")
def test_clean_kernel_sum_close_to_zero_raises_error():
    image = np.random.randn(100, 100)
    npixels, nlevels, nsigma, num_peaks, num_peaks_per_label, contrast, min_distance = 5, 32, 3, 3, 2, 0.001, 3  # Any dummy values.
    kernel = Gaussian2DKernel(2).array
    kernel /= 1e9  # Make kernel values very small

    with pytest.raises(ValueError) as excinfo:
        galMask(
            image, npixels, nlevels, nsigma, contrast, min_distance,
            num_peaks, num_peaks_per_label, kernel=kernel
        )

    assert (
        "Kernel sum is close to zero. Cannot use it for convolution." in excinfo.exconly()
    )

@pytest.mark.filterwarnings("ignore::UserWarning")
@pytest.mark.filterwarnings("ignore::photutils.utils.exceptions.NoDetectionsWarning")
def test_raises_error_if_no_source_detected():
    image = np.random.randn(100, 100)  # Gaussian array with no source.
    npixels, nlevels, nsigma, num_peaks, num_peaks_per_label, contrast, min_distance = 5, 32, 3, 3, 2, 0.001, 3  # Any dummy values.

    with pytest.raises(ValueError) as excinfo:
        galMask(
            image, npixels, nlevels, nsigma, contrast, min_distance,
            num_peaks, num_peaks_per_label
        )
    assert (
        "No source detection found in the image!" in excinfo.exconly()
    )

def test_kernel_not_normalized_raises_warning():
    image = make_100gaussians_image()
    npixels, nlevels, nsigma, num_peaks, num_peaks_per_label, contrast, min_distance = 5, 32, 3, 3, 2, 0.001, 3  # Any dummy values.
    kernel = Gaussian2DKernel(2).array

    with pytest.warns():
        galMask(
            image, npixels, nlevels, nsigma, contrast, min_distance,
            num_peaks, num_peaks_per_label, kernel=kernel
        )
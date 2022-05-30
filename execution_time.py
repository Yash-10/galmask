import timeit

setup  = '''
from galmask.galmask import galmask
from astropy.io import fits
npixels, nlevels, nsigma, contrast, min_distance, num_peaks, num_peaks_per_label, connectivity, remove_local_max = 5, 32, 3., 0.001, 1, 10, 3, 4, True
seg_image=fits.open('example/gal_segment.fits')[3].data
image=image=fits.getdata('example/gal.fits')
kernel=fits.getdata('example/kernel.fits')
'''


stmt = '''
galmask(
image, npixels, nlevels, nsigma, contrast, min_distance, num_peaks, num_peaks_per_label, connectivity=connectivity, remove_local_max=remove_local_max, seg_image=seg_image, kernel=kernel
)
'''

timeit.repeat(stmt, setup=setup, number=100, repeat=5)

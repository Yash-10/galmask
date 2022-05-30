from timeit import default_timer as timer
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.visualization import AsinhStretch, ImageNormalize, ZScaleInterval

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

plt.rc('font', family='sans-serif')

from galmask.galmask import galmask

def axes_colorbar(ax):
    divider = make_axes_locatable(ax)
    cax = divider.append_axes('bottom', size='5%', pad=0.05)
    return cax

filepath = 'gal.fits'
image = fits.getdata(filepath)
npixels, nlevels, nsigma, contrast, min_distance, num_peaks, num_peaks_per_label, connectivity, remove_local_max = 5, 32, 3., 0.001, 1, 10, 3, 4, True
hdul = fits.open('gal_segment.fits')
objects = hdul[3].data
seg_image = objects.astype('uint8')

start = timer()
galmasked, galsegmap = galmask(
    image, npixels, nlevels, nsigma, contrast, min_distance, num_peaks, num_peaks_per_label,
    connectivity=4, kernel=fits.getdata('kernel.fits'), seg_image=seg_image, mode="2",
    remove_local_max=True, deblend=True
)
end = timer()

print(f'Execution time: {end-start}s')

fig, ax = plt.subplots(1, 4, figsize=(24, 6))

# fig.suptitle(filepath)
norm1 = ImageNormalize(image, interval=ZScaleInterval(), stretch=AsinhStretch())
im0 = ax[0].imshow(image, norm=norm1, origin='lower')
ax[0].set_title("Original image")
cax0 = axes_colorbar(ax[0])
fig.colorbar(im0, cax=cax0, orientation='horizontal')

im1 = ax[1].imshow(objects, origin='lower')
ax[1].set_title("Original segmentation map (NoiseChisel)")
cax1 = axes_colorbar(ax[1])
fig.colorbar(im1, cax=cax1, orientation='horizontal')

im2 = ax[2].imshow(galsegmap, origin='lower')
ax[2].set_title("Final segmentation map (galmask)")
cax2 = axes_colorbar(ax[2])
fig.colorbar(im2, cax=cax2, orientation='horizontal')

norm2 = ImageNormalize(galmasked, stretch=AsinhStretch())
im3 = ax[3].imshow(galmasked, norm=norm2, origin='lower')
ax[3].set_title("Final image (galmask)")
cax3 = axes_colorbar(ax[3])
fig.colorbar(im3, cax=cax3, orientation='horizontal')

plt.savefig('galmask_example.png', bbox_inches='tight', dpi=400)

plt.show()

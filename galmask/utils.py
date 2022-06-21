import numpy as np

from skimage.measure import label, regionprops


# Below two functions are faster than numpy for small coordinate arrays.
def find_farthest_label(coords, refx, refy):  # TODO: This function is slow and inefficient -- rewrite using standard libraries.
    """Find coordinate (i.e. row) with maximum distance from the reference coordinate, (refx, refy).
    
    :param coords: 2d coordinate array with each row denoting a coordinate (x, y).
    :type coords: numpy.ndarray
    :param refx: Reference x coordinate.
    :type refx: float
    :param refy: Reference y coordinate.
    :type refy: float

    :return max_index: Index corresponding to maximum distance.
    :rtype: int

    """
    refcoord = np.array((refx, refy))
    distances = np.linalg.norm(coords - refcoord, axis=1)
    max_index = np.argmax(distances)
    return max_index

def find_closest_label(coords, refx, refy):
    """Find coordinate (i.e. row) with minimum distance from the reference coordinate, (refx, refy).
    
    :param coords: 2d coordinate array with each row denoting a coordinate (x, y).
    :type coords: numpy.ndarray
    :param refx: Reference x coordinate.
    :type refx: float
    :param refy: Reference y coordinate.
    :type refy: float

    :return max_index: Index corresponding to minimum distance.
    :rtype: int

    """
    refcoord = np.array((refx, refy))
    distances = np.linalg.norm(coords - refcoord, axis=1)
    min_index = np.argmin(distances)
    return min_index + 1

def getLargestCC(segmentation):
    """Find the largest connected component (CC) from a segmentation image.

    :param segmentation: Segmentation map
    :type segmentation: numpy.ndarray

    :return largestCC: Boolean array containing the largest connected component.
    :rtype: numpy.ndarray

    """
    # From https://stackoverflow.com/questions/47540926/get-the-largest-connected-component-of-segmentation-image
    labels = label(segmentation)
    assert labels.max() != 0, "There must be atleast one connected component in the segmentation image!"
    largestCC = labels == np.argmax(np.bincount(labels.flat)[1:]) + 1
    return largestCC

def getCenterLabelRegion(objects):
    _img_shape = objects.shape
    _num_labels = len(np.unique(objects)) - 1  # Ignore background label (= 0).
    props = regionprops(objects)
    centroids = np.array([props[i].centroid for i in range(_num_labels)])
    areas = np.array([props[i].area for i in range(_num_labels)])
    max_label = props[np.argmax(areas)].label   # Need to add one since regionprops ignores background label 0.
    closest_to_center_label = find_closest_label(centroids, _img_shape[0]/2, _img_shape[1]/2)

    if max_label == props[closest_to_center_label-1].label:
        x = (objects == max_label).astype(float)
    else:
        x = (objects == closest_to_center_label).astype(float)
    return x

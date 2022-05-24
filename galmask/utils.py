import numpy as np

from skimage.measure import label


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
    max_dist = -np.Inf
    max_index = -99
    for i in range(coords.shape[0]):
        dist = abs(coords[i][0] - refx) + abs(coords[i][1] - refy)
        if dist > max_dist:
            max_dist = dist
            max_index = i

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
    min_dist = np.Inf
    min_index = 99999
    for i in range(coords.shape[0]):
        dist = abs(coords[i][0] - refy) + abs(coords[i][1] - refx)
        if dist < min_dist:
            min_dist = dist
            min_index = i

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

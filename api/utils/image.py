"""
This module provides functions for manipulating images.
"""

from PIL import Image

"""
                        IMAGE THUMBNAIL
"""

def flat(*nums):
    """
    Create a tuple out of the `height` and `width`.
    """
    return tuple(int(round(n)) for n in nums)


class Size(object):
    """
    Represent a size with a given `width` and `height`.
    """
    def __init__(self, pair):
        self.width = float(pair[0])
        self.height = float(pair[1])

    @property
    def aspect_ratio(self):
        """
        Return the aspect_ratio.
        """
        return self.width /self.height
    
    @property
    def size(self):
        """
        Return the size.
        """
        return flat(self.width, self.height)

def thumbnail(img, size):
    """
    Return a `Pillow` thumbnail that has been created from the given `img`.
    """
    original = Size(img.size)
    target = Size(size)
     
    if target.aspect_ratio > original.aspect_ratio:
        scale_factor = target.width / original.width
        crop_size = Size( (original.width, target.height / scale_factor) )
        top_cut_line = 0
        img = img.crop( flat(0, top_cut_line, crop_size.width, top_cut_line + crop_size.height) )
    elif target.aspect_ratio < original.aspect_ratio:
        scale_factor = target.height / original.height
        crop_size = Size( (target.width/scale_factor, original.height) )
        side_cut_line = (original.width - crop_size.width) / 2
        img = img.crop( flat(side_cut_line, 0, side_cut_line + crop_size.width, crop_size.height) )

    return img.resize(target.size, Image.ANTIALIAS)

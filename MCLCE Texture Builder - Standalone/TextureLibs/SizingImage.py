from PIL import Image, ImageFilter
import math
import warnings

# what functions change in this file?
    # new
    # crop
    # resize
    # paste
    # alpha_composite

processingSize = 16 # an integer (default 16)
baseSize = 16
maxSize = 64
def getMultiplier() -> float:
    return processingSize / baseSize

def resizingNeeded():
    return (getMultiplier() != float(1))

def convertTuple(tup):
    if (not (type(tup) is tuple)): print("conversion error -convertTuple"); exit()
    if (not resizingNeeded()): return tup # check if resizing is needed
    i = 0
    tup = list(tup)
    while i < len(tup):
        tup[i] = int(tup[i] * getMultiplier())
        i += 1
    return tuple(tup)

def deconvertTuple(tup):
    if (not (type(tup) is tuple)): print("conversion error -deconvertTuple"); exit()
    if (not resizingNeeded()): return tup # check if resizing is needed
    i = 0
    tup = list(tup)
    while i < len(tup):
        tup[i] = int(tup[i] / getMultiplier())
        i += 1
    return tuple(tup)

def convertInt(num):
    if (not (type(num) is int)): print("conversion error -convertInt"); exit()
    if (not resizingNeeded()): return num # check if resizing is needed
    return int(num * getMultiplier())

def deconvertInt(num):
    if (not (type(num) is int)): print("conversion error -deconvertInt"); exit()
    if (not resizingNeeded()): return num # check if resizing is needed
    return int(num / getMultiplier())

def changeProcessingSize(num):
    """
    Description:
        Changes the processing size and dynamically checks if the size is between the min and max range without reading a specific list of possible values
    """
    if (verifyPowerOfTwo(num, "processing") == True):
        global processingSize
        processingSize = num

# --- Utility ---

def verifyPowerOfTwo(num, variableName=None, *, overrideMinimum=16):
    """
    Description:
        Verifies if a value is a power of two within the min-max range
    ---
    Arguments:
        - num : Integer <>
        - variableName : String <None>
            - The name of variable, strictly used or error printing
        - overrideMinimum : Integer <0>
            - Changes the minimum allowed multiplier (log) range value 
    ---
    Returns:
        Boolean
    """
    # spacing
    if (not variableName.endswith(" ")): variableName = f"{variableName} "

    # variables and checks
    overrideMinimum = math.log2(overrideMinimum) - math.log2(baseSize) # converts to multiplier-like value
    proposedMultiplier = math.log2(num) - math.log2(baseSize) # contextualize the num's multiplier with the max size multiplier
    rangeOfLogOutput = math.log2(maxSize) - math.log2(baseSize) # get the range of possible outputs
    if (proposedMultiplier > rangeOfLogOutput): # checks if the num is in the the range (baseSize to maxSize)
        print(f"{variableName}size is too large. Input: {num} when the max size is {maxSize}")
        exit()
    if (int(proposedMultiplier) != proposedMultiplier): # checks if the num is a power of 2
        print(f"{variableName}size is not a power of 2. Values must be a power of two or similar (ex. '16', '32', '64')")
        exit()
    if (proposedMultiplier < overrideMinimum): # checks if the number is negative (negative would mean below 16)
        print(f"{variableName}size is too small. Minimum size is {baseSize}")
        exit()
    return True


class SizingImage():
    def __init__(self, img): # constructor
        self._img=img
    def __getattr__(self,key): # get attributes
        if key == '_img':
            raise AttributeError()
        return getattr(self._img,key)
    def new(mode, size, color=0, doResize=True):
        # changes
        if doResize == True:
            size = convertTuple(size)

        # NO CHANGE
        """
        Creates a new image with the given mode and size.

        :param mode: The mode to use for the new image. See:
        :ref:`concept-modes`.
        :param size: A 2-tuple, containing (width, height) in pixels.
        :param color: What color to use for the image.  Default is black.
        If given, this should be a single integer or floating point value
        for single-band modes, and a tuple for multi-band modes (one value
        per band).  When creating RGB or HSV images, you can also use color
        strings as supported by the ImageColor module.  If the color is
        None, the image is not initialised.
        :returns: An :py:class:`~PIL.Image.Image` object.
        """
        
        return SizingImage(Image.new(mode, size, color))
    def open(fp, mode="r", formats=None):
        # NO CHANGE
        """
        Opens and identifies the given image file.

        This is a lazy operation; this function identifies the file, but
        the file remains open and the actual image data is not read from
        the file until you try to process the data (or call the
        :py:meth:`~PIL.Image.Image.load` method).  See
        :py:func:`~PIL.Image.new`. See :ref:`file-handling`.

        :param fp: A filename (string), pathlib.Path object or a file object.
        The file object must implement ``file.read``,
        ``file.seek``, and ``file.tell`` methods,
        and be opened in binary mode. The file object will also seek to zero
        before reading.
        :param mode: The mode.  If given, this argument must be "r".
        :param formats: A list or tuple of formats to attempt to load the file in.
        This can be used to restrict the set of formats checked.
        Pass ``None`` to try all supported formats. You can print the set of
        available formats by running ``python3 -m PIL`` or using
        the :py:func:`PIL.features.pilinfo` function.
        :returns: An :py:class:`~PIL.Image.Image` object.
        :exception FileNotFoundError: If the file cannot be found.
        :exception PIL.UnidentifiedImageError: If the image cannot be opened and
        identified.
        :exception ValueError: If the ``mode`` is not "r", or if a ``StringIO``
        instance is used for ``fp``.
        :exception TypeError: If ``formats`` is not ``None``, a list or a tuple.
        """
        
        return SizingImage(Image.open(fp, mode, formats))
    def crop(self, box=None, doResize=True):
        # changes
        if doResize == True:
            box = convertTuple(box)

        # NO CHANGE
        """
        Returns a rectangular region from this image. The box is a
        4-tuple defining the left, upper, right, and lower pixel
        coordinate. See :ref:`coordinate-system`.

        Note: Prior to Pillow 3.4.0, this was a lazy operation.

        :param box: The crop rectangle, as a (left, upper, right, lower)-tuple.
        :rtype: :py:class:`~PIL.Image.Image`
        :returns: An :py:class:`~PIL.Image.Image` object.
        """

        if box is None:
            return SizingImage(self.copy())

        if box[2] < box[0]:
            msg = "Coordinate 'right' is less than 'left'"
            raise ValueError(msg)
        elif box[3] < box[1]:
            msg = "Coordinate 'lower' is less than 'upper'"
            raise ValueError(msg)

        self.load()
        return SizingImage(self._new(self._crop(self.im, box)))
    def resize(self, size, resample=Image.NEAREST, box=None, reducing_gap=None, doResize=True):
        # changes
            # sampling now defaults to NEAREST
        if doResize == True:
            size = convertTuple(size)

        # NO CHANGE
        """
        Returns a resized copy of this image.

        :param size: The requested size in pixels, as a 2-tuple:
           (width, height).
        :param resample: An optional resampling filter.  This can be
           one of :py:data:`Resampling.NEAREST`, :py:data:`Resampling.BOX`,
           :py:data:`Resampling.BILINEAR`, :py:data:`Resampling.HAMMING`,
           :py:data:`Resampling.BICUBIC` or :py:data:`Resampling.LANCZOS`.
           If the image has mode "1" or "P", it is always set to
           :py:data:`Resampling.NEAREST`. If the image mode specifies a number
           of bits, such as "I;16", then the default filter is
           :py:data:`Resampling.NEAREST`. Otherwise, the default filter is
           :py:data:`Resampling.BICUBIC`. See: :ref:`concept-filters`.
        :param box: An optional 4-tuple of floats providing
           the source image region to be scaled.
           The values must be within (0, 0, width, height) rectangle.
           If omitted or None, the entire source is used.
        :param reducing_gap: Apply optimization by resizing the image
           in two steps. First, reducing the image by integer times
           using :py:meth:`~PIL.Image.Image.reduce`.
           Second, resizing using regular resampling. The last step
           changes size no less than by ``reducing_gap`` times.
           ``reducing_gap`` may be None (no first step is performed)
           or should be greater than 1.0. The bigger ``reducing_gap``,
           the closer the result to the fair resampling.
           The smaller ``reducing_gap``, the faster resizing.
           With ``reducing_gap`` greater or equal to 3.0, the result is
           indistinguishable from fair resampling in most cases.
           The default value is None (no optimization).
        :returns: An :py:class:`~PIL.Image.Image` object.
        """

        if resample is None:
            type_special = ";" in self.mode
            resample = Image.Resampling.NEAREST if type_special else Image.Resampling.BICUBIC
        elif resample not in (
            Image.Resampling.NEAREST,
            Image.Resampling.BILINEAR,
            Image.Resampling.BICUBIC,
            Image.Resampling.LANCZOS,
            Image.Resampling.BOX,
            Image.Resampling.HAMMING,
        ):
            msg = f"Unknown resampling filter ({resample})."

            filters = [
                f"{filter[1]} ({filter[0]})"
                for filter in (
                    (Image.Resampling.NEAREST, "Image.Resampling.NEAREST"),
                    (Image.Resampling.LANCZOS, "Image.Resampling.LANCZOS"),
                    (Image.Resampling.BILINEAR, "Image.Resampling.BILINEAR"),
                    (Image.Resampling.BICUBIC, "Image.Resampling.BICUBIC"),
                    (Image.Resampling.BOX, "Image.Resampling.BOX"),
                    (Image.Resampling.HAMMING, "Image.Resampling.HAMMING"),
                )
            ]
            msg += " Use " + ", ".join(filters[:-1]) + " or " + filters[-1]
            raise ValueError(msg)

        if reducing_gap is not None and reducing_gap < 1.0:
            msg = "reducing_gap must be 1.0 or greater"
            raise ValueError(msg)

        size = tuple(size)

        self.load()
        if box is None:
            box = (0, 0) + self.size
        else:
            box = tuple(box)

        if self.size == size and box == (0, 0) + self.size:
            return SizingImage(self.copy())

        if self.mode in ("1", "P"):
            resample = Image.Resampling.NEAREST

        if self.mode in ["LA", "RGBA"] and resample != Image.Resampling.NEAREST:
            im = self.convert({"LA": "La", "RGBA": "RGBa"}[self.mode])
            im = im.resize(size, resample, box, doResize=False)
            return SizingImage(im.convert(self.mode))

        self.load()

        if reducing_gap is not None and resample != Image.Resampling.NEAREST:
            factor_x = int((box[2] - box[0]) / size[0] / reducing_gap) or 1
            factor_y = int((box[3] - box[1]) / size[1] / reducing_gap) or 1
            if factor_x > 1 or factor_y > 1:
                reduce_box = self._get_safe_box(size, resample, box)
                factor = (factor_x, factor_y)
                if callable(self.reduce):
                    self = self.reduce(factor, box=reduce_box)
                else:
                    self = Image.reduce(self, factor, box=reduce_box)
                box = (
                    (box[0] - reduce_box[0]) / factor_x,
                    (box[1] - reduce_box[1]) / factor_y,
                    (box[2] - reduce_box[0]) / factor_x,
                    (box[3] - reduce_box[1]) / factor_y,
                )

        return SizingImage(self._new(self.im.resize(size, resample, box)))
    def paste(self, im, box=None, mask=None, mode="RGBA", doResize=True):
        # changes
        if (doResize == True) and (box != None):
            box = convertTuple(box)

        # mode conversion
        im = im.convert(mode)

        # NO CHANGE 
        """
        Pastes another image into this image. The box argument is either
        a 2-tuple giving the upper left corner, a 4-tuple defining the
        left, upper, right, and lower pixel coordinate, or None (same as
        (0, 0)). See :ref:`coordinate-system`. If a 4-tuple is given, the size
        of the pasted image must match the size of the region.

        If the modes don't match, the pasted image is converted to the mode of
        this image (see the :py:meth:`~PIL.Image.Image.convert` method for
        details).

        Instead of an image, the source can be a integer or tuple
        containing pixel values.  The method then fills the region
        with the given color.  When creating RGB images, you can
        also use color strings as supported by the ImageColor module.

        If a mask is given, this method updates only the regions
        indicated by the mask. You can use either "1", "L", "LA", "RGBA"
        or "RGBa" images (if present, the alpha band is used as mask).
        Where the mask is 255, the given image is copied as is.  Where
        the mask is 0, the current value is preserved.  Intermediate
        values will mix the two images together, including their alpha
        channels if they have them.

        See :py:meth:`~PIL.Image.Image.alpha_composite` if you want to
        combine images with respect to their alpha channels.

        :param im: Source image or pixel value (integer or tuple).
        :param box: An optional 4-tuple giving the region to paste into.
           If a 2-tuple is used instead, it's treated as the upper left
           corner.  If omitted or None, the source is pasted into the
           upper left corner.

           If an image is given as the second argument and there is no
           third, the box defaults to (0, 0), and the second argument
           is interpreted as a mask image.
        :param mask: An optional mask image.
        """

        if Image.isImageType(box) and mask is None:
            # abbreviated paste(im, mask) syntax
            mask = box
            box = None

        if box is None:
            box = (0, 0)

        if len(box) == 2:
            # upper left corner given; get size from image or mask
            if Image.isImageType(im):
                size = im.size
            elif Image.isImageType(mask):
                size = mask.size
            else:
                # FIXME: use self.size here?
                msg = "cannot determine region size; use 4-item box"
                raise ValueError(msg)
            box += (box[0] + size[0], box[1] + size[1])

        if isinstance(im, str):
            from .. import ImageColor

            im = ImageColor.getcolor(im, self.mode)

        elif Image.isImageType(im):
            im.load()
            if self.mode != im.mode:
                if self.mode != "RGB" or im.mode not in ("LA", "RGBA", "RGBa"):
                    # should use an adapter for this!
                    im = im.convert(self.mode)
            im = im.im

        self._ensure_mutable()

        if mask:
            mask.load()
            self.im.paste(im, box, mask.im)
        else:
            self.im.paste(im, box)
    def alpha_composite(self, im, dest=(0, 0), source=(0, 0), mode="RGBA", doResize=True):
        # changes
        if doResize == True:
            dest = convertTuple(dest)
            source = convertTuple(source)

        # mode conversion
        im = im.convert(mode)

        # NO CHANGE
        """'In-place' analog of Image.alpha_composite. Composites an image
        onto this image.

        :param im: image to composite over this one
        :param dest: Optional 2 tuple (left, top) specifying the upper
          left corner in this (destination) image.
        :param source: Optional 2 (left, top) tuple for the upper left
          corner in the overlay source image, or 4 tuple (left, top, right,
          bottom) for the bounds of the source rectangle

        Performance Note: Not currently implemented in-place in the core layer.
        """

        if not isinstance(source, (list, tuple)):
            msg = "Source must be a tuple"
            raise ValueError(msg)
        if not isinstance(dest, (list, tuple)):
            msg = "Destination must be a tuple"
            raise ValueError(msg)
        if len(source) not in (2, 4):
            msg = "Source must be a 2 or 4-tuple"
            raise ValueError(msg)
        if not len(dest) == 2:
            msg = "Destination must be a 2-tuple"
            raise ValueError(msg)
        if min(source) < 0:
            msg = "Source must be non-negative"
            raise ValueError(msg)

        if len(source) == 2:
            source = source + im.size

        # over image, crop if it's not the whole thing.
        if source == (0, 0) + im.size:
            overlay = im
        else:
            overlay = im.crop(source)

        # target for the paste
        box = dest + (dest[0] + overlay.width, dest[1] + overlay.height)

        # destination image. don't copy if we're using the whole image.
        if box == (0, 0) + self.size:
            background = self
        else:
            background = self.crop(box, doResize=False)

        result = Image.alpha_composite(background, overlay)
        self.paste(result, box, doResize=False)
    def show(self, title=None):
        # NO CHANGE
        """
        Displays this image. This method is mainly intended for debugging purposes.

        This method calls :py:func:`PIL.ImageShow.show` internally. You can use
        :py:func:`PIL.ImageShow.register` to override its default behaviour.

        The image is first saved to a temporary file. By default, it will be in
        PNG format.

        On Unix, the image is then opened using the **xdg-open**, **display**,
        **gm**, **eog** or **xv** utility, depending on which one can be found.

        On macOS, the image is opened with the native Preview application.

        On Windows, the image is opened with the standard PNG display utility.

        :param title: Optional title to use for the image window, where possible.
        """

        Image._show(self, title=title)
    def rotate(
        self,
        angle,
        resample=Image.Resampling.NEAREST,
        expand=0,
        center=None,
        translate=None,
        fillcolor=None,
    ):
        # NO CHANGE
        """
        Returns a rotated copy of this image.  This method returns a
        copy of this image, rotated the given number of degrees counter
        clockwise around its centre.

        :param angle: In degrees counter clockwise.
        :param resample: An optional resampling filter.  This can be
           one of :py:data:`Resampling.NEAREST` (use nearest neighbour),
           :py:data:`Resampling.BILINEAR` (linear interpolation in a 2x2
           environment), or :py:data:`Resampling.BICUBIC` (cubic spline
           interpolation in a 4x4 environment). If omitted, or if the image has
           mode "1" or "P", it is set to :py:data:`Resampling.NEAREST`.
           See :ref:`concept-filters`.
        :param expand: Optional expansion flag.  If true, expands the output
           image to make it large enough to hold the entire rotated image.
           If false or omitted, make the output image the same size as the
           input image.  Note that the expand flag assumes rotation around
           the center and no translation.
        :param center: Optional center of rotation (a 2-tuple).  Origin is
           the upper left corner.  Default is the center of the image.
        :param translate: An optional post-rotate translation (a 2-tuple).
        :param fillcolor: An optional color for area outside the rotated image.
        :returns: An :py:class:`~PIL.Image.Image` object.
        """

        angle = angle % 360.0

        # Fast paths regardless of filter, as long as we're not
        # translating or changing the center.
        if not (center or translate):
            if angle == 0:
                return SizingImage(self.copy())
            if angle == 180:
                return SizingImage(self.transpose(Image.Transpose.ROTATE_180))
            if angle in (90, 270) and (expand or self.width == self.height):
                return SizingImage(self.transpose(
                    Image.Transpose.ROTATE_90 if angle == 90 else Image.Transpose.ROTATE_270)
                )

        # Calculate the affine matrix.  Note that this is the reverse
        # transformation (from destination image to source) because we
        # want to interpolate the (discrete) destination pixel from
        # the local area around the (floating) source pixel.

        # The matrix we actually want (note that it operates from the right):
        # (1, 0, tx)   (1, 0, cx)   ( cos a, sin a, 0)   (1, 0, -cx)
        # (0, 1, ty) * (0, 1, cy) * (-sin a, cos a, 0) * (0, 1, -cy)
        # (0, 0,  1)   (0, 0,  1)   (     0,     0, 1)   (0, 0,   1)

        # The reverse matrix is thus:
        # (1, 0, cx)   ( cos -a, sin -a, 0)   (1, 0, -cx)   (1, 0, -tx)
        # (0, 1, cy) * (-sin -a, cos -a, 0) * (0, 1, -cy) * (0, 1, -ty)
        # (0, 0,  1)   (      0,      0, 1)   (0, 0,   1)   (0, 0,   1)

        # In any case, the final translation may be updated at the end to
        # compensate for the expand flag.

        w, h = self.size

        if translate is None:
            post_trans = (0, 0)
        else:
            post_trans = translate
        if center is None:
            # FIXME These should be rounded to ints?
            rotn_center = (w / 2.0, h / 2.0)
        else:
            rotn_center = center

        angle = -math.radians(angle)
        matrix = [
            round(math.cos(angle), 15),
            round(math.sin(angle), 15),
            0.0,
            round(-math.sin(angle), 15),
            round(math.cos(angle), 15),
            0.0,
        ]

        def transform(x, y, matrix):
            (a, b, c, d, e, f) = matrix
            return a * x + b * y + c, d * x + e * y + f

        matrix[2], matrix[5] = transform(
            -rotn_center[0] - post_trans[0], -rotn_center[1] - post_trans[1], matrix
        )
        matrix[2] += rotn_center[0]
        matrix[5] += rotn_center[1]

        if expand:
            # calculate output size
            xx = []
            yy = []
            for x, y in ((0, 0), (w, 0), (w, h), (0, h)):
                x, y = transform(x, y, matrix)
                xx.append(x)
                yy.append(y)
            nw = math.ceil(max(xx)) - math.floor(min(xx))
            nh = math.ceil(max(yy)) - math.floor(min(yy))

            # We multiply a translation matrix from the right.  Because of its
            # special form, this is the same as taking the image of the
            # translation vector as new translation vector.
            matrix[2], matrix[5] = transform(-(nw - w) / 2.0, -(nh - h) / 2.0, matrix)
            w, h = nw, nh

        return SizingImage(self.transform(
            (w, h), Image.Transform.AFFINE, matrix, resample, fillcolor=fillcolor
        ))
    def convert(
        self, mode=None, matrix=None, dither=None, palette=Image.Palette.WEB, colors=256
    ):
        # NO CHANGE
        """
        Returns a converted copy of this image. For the "P" mode, this
        method translates pixels through the palette.  If mode is
        omitted, a mode is chosen so that all information in the image
        and the palette can be represented without a palette.

        The current version supports all possible conversions between
        "L", "RGB" and "CMYK". The ``matrix`` argument only supports "L"
        and "RGB".

        When translating a color image to greyscale (mode "L"),
        the library uses the ITU-R 601-2 luma transform::

            L = R * 299/1000 + G * 587/1000 + B * 114/1000

        The default method of converting a greyscale ("L") or "RGB"
        image into a bilevel (mode "1") image uses Floyd-Steinberg
        dither to approximate the original image luminosity levels. If
        dither is ``None``, all values larger than 127 are set to 255 (white),
        all other values to 0 (black). To use other thresholds, use the
        :py:meth:`~PIL.Image.Image.point` method.

        When converting from "RGBA" to "P" without a ``matrix`` argument,
        this passes the operation to :py:meth:`~PIL.Image.Image.quantize`,
        and ``dither`` and ``palette`` are ignored.

        When converting from "PA", if an "RGBA" palette is present, the alpha
        channel from the image will be used instead of the values from the palette.

        :param mode: The requested mode. See: :ref:`concept-modes`.
        :param matrix: An optional conversion matrix.  If given, this
           should be 4- or 12-tuple containing floating point values.
        :param dither: Dithering method, used when converting from
           mode "RGB" to "P" or from "RGB" or "L" to "1".
           Available methods are :data:`Dither.NONE` or :data:`Dither.FLOYDSTEINBERG`
           (default). Note that this is not used when ``matrix`` is supplied.
        :param palette: Palette to use when converting from mode "RGB"
           to "P".  Available palettes are :data:`Palette.WEB` or
           :data:`Palette.ADAPTIVE`.
        :param colors: Number of colors to use for the :data:`Palette.ADAPTIVE`
           palette. Defaults to 256.
        :rtype: :py:class:`~PIL.Image.Image`
        :returns: An :py:class:`~PIL.Image.Image` object.
        """

        self.load()

        has_transparency = "transparency" in self.info
        if not mode and self.mode == "P":
            # determine default mode
            if self.palette:
                mode = self.palette.mode
            else:
                mode = "RGB"
            if mode == "RGB" and has_transparency:
                mode = "RGBA"
        if not mode or (mode == self.mode and not matrix):
            return SizingImage(self.copy())

        if matrix:
            # matrix conversion
            if mode not in ("L", "RGB"):
                msg = "illegal conversion"
                raise ValueError(msg)
            im = self.im.convert_matrix(mode, matrix)
            new_im = self._new(im)
            if has_transparency and self.im.bands == 3:
                transparency = new_im.info["transparency"]

                def convert_transparency(m, v):
                    v = m[0] * v[0] + m[1] * v[1] + m[2] * v[2] + m[3] * 0.5
                    return max(0, min(255, int(v)))

                if mode == "L":
                    transparency = convert_transparency(matrix, transparency)
                elif len(mode) == 3:
                    transparency = tuple(
                        convert_transparency(matrix[i * 4 : i * 4 + 4], transparency)
                        for i in range(0, len(transparency))
                    )
                new_im.info["transparency"] = transparency
            return SizingImage(new_im)

        if mode == "P" and self.mode == "RGBA":
            return SizingImage(self.quantize(colors))

        trns = None
        delete_trns = False
        # transparency handling
        if has_transparency:
            if (self.mode in ("1", "L", "I") and mode in ("LA", "RGBA")) or (
                self.mode == "RGB" and mode == "RGBA"
            ):
                # Use transparent conversion to promote from transparent
                # color to an alpha channel.
                new_im = self._new(
                    self.im.convert_transparent(mode, self.info["transparency"])
                )
                del new_im.info["transparency"]
                return SizingImage(new_im)
            elif self.mode in ("L", "RGB", "P") and mode in ("L", "RGB", "P"):
                t = self.info["transparency"]
                if isinstance(t, bytes):
                    # Dragons. This can't be represented by a single color
                    warnings.warn(
                        "Palette images with Transparency expressed in bytes should be "
                        "converted to RGBA images"
                    )
                    delete_trns = True
                else:
                    # get the new transparency color.
                    # use existing conversions
                    trns_im = Image.new(self.mode, (1, 1))
                    if self.mode == "P":
                        trns_im.putpalette(self.palette)
                        if isinstance(t, tuple):
                            err = "Couldn't allocate a palette color for transparency"
                            try:
                                t = trns_im.palette.getcolor(t, self)
                            except ValueError as e:
                                if str(e) == "cannot allocate more than 256 colors":
                                    # If all 256 colors are in use,
                                    # then there is no need for transparency
                                    t = None
                                else:
                                    raise ValueError(err) from e
                    if t is None:
                        trns = None
                    else:
                        trns_im.putpixel((0, 0), t)

                        if mode in ("L", "RGB"):
                            trns_im = trns_im.convert(mode)
                        else:
                            # can't just retrieve the palette number, got to do it
                            # after quantization.
                            trns_im = trns_im.convert("RGB")
                        trns = trns_im.getpixel((0, 0))

            elif self.mode == "P" and mode in ("LA", "PA", "RGBA"):
                t = self.info["transparency"]
                delete_trns = True

                if isinstance(t, bytes):
                    self.im.putpalettealphas(t)
                elif isinstance(t, int):
                    self.im.putpalettealpha(t, 0)
                else:
                    msg = "Transparency for P mode should be bytes or int"
                    raise ValueError(msg)

        if mode == "P" and palette == Image.Palette.ADAPTIVE:
            im = self.im.quantize(colors)
            new_im = self._new(im)
            from .. import ImagePalette

            new_im.palette = ImagePalette.ImagePalette(
                "RGB", new_im.im.getpalette("RGB")
            )
            if delete_trns:
                # This could possibly happen if we requantize to fewer colors.
                # The transparency would be totally off in that case.
                del new_im.info["transparency"]
            if trns is not None:
                try:
                    new_im.info["transparency"] = new_im.palette.getcolor(trns, new_im)
                except Exception:
                    # if we can't make a transparent color, don't leave the old
                    # transparency hanging around to mess us up.
                    del new_im.info["transparency"]
                    warnings.warn("Couldn't allocate palette entry for transparency")
            return SizingImage(new_im)

        if "LAB" in (self.mode, mode):
            other_mode = mode if self.mode == "LAB" else self.mode
            if other_mode in ("RGB", "RGBA", "RGBX"):
                from .. import ImageCms

                srgb = ImageCms.createProfile("sRGB")
                lab = ImageCms.createProfile("LAB")
                profiles = [lab, srgb] if self.mode == "LAB" else [srgb, lab]
                transform = ImageCms.buildTransform(
                    profiles[0], profiles[1], self.mode, mode
                )
                return SizingImage(transform.apply(self))

        # colorspace conversion
        if dither is None:
            dither = Image.Dither.FLOYDSTEINBERG

        try:
            im = self.im.convert(mode, dither)
        except ValueError:
            try:
                # normalize source image and try again
                modebase = Image.getmodebase(self.mode)
                if modebase == self.mode:
                    raise
                im = self.im.convert(modebase)
                im = im.convert(mode, dither)
            except KeyError as e:
                msg = "illegal conversion"
                raise ValueError(msg) from e

        new_im = self._new(im)
        if mode == "P" and palette != Image.Palette.ADAPTIVE:
            from .. import ImagePalette

            new_im.palette = ImagePalette.ImagePalette("RGB", im.getpalette("RGB"))
        if delete_trns:
            # crash fail if we leave a bytes transparency in an rgb/l mode.
            del new_im.info["transparency"]
        if trns is not None:
            if new_im.mode == "P":
                try:
                    new_im.info["transparency"] = new_im.palette.getcolor(trns, new_im)
                except ValueError as e:
                    del new_im.info["transparency"]
                    if str(e) != "cannot allocate more than 256 colors":
                        # If all 256 colors are in use,
                        # then there is no need for transparency
                        warnings.warn(
                            "Couldn't allocate palette entry for transparency"
                        )
            else:
                new_im.info["transparency"] = trns
        return SizingImage(new_im)
    def copy(self):
        """
        Copies this image. Use this method if you wish to paste things
        into an image, but still retain the original.

        :rtype: :py:class:`~PIL.Image.Image`
        :returns: An :py:class:`~PIL.Image.Image` object.
        """
        self.load()
        return SizingImage(self._new(self.im.copy()))
    
    def gaussianBlur(image, radius):
        # image for generation: the sizing image is copied into a normal image so it can be processed with PIL gaussian blur algorithms
        normalImage = Image.new("RGBA", image.size)

        # for every pixel
        i = 0
        while i < image.width:
            j = 0
            while j < image.height:
                normalImage.putpixel((i, j), image.getpixel((i, j))) # copies the image's color

                j += 1
            i += 1

        return SizingImage(normalImage.filter(ImageFilter.GaussianBlur(radius=radius)))



class SizingImageOps():
    def flip(image):
        # NO CHANGE
        """
        Flip the image vertically (top to bottom).

        :param image: The image to flip.
        :return: An image.
        """
        return SizingImage(image.transpose(Image.Transpose.FLIP_TOP_BOTTOM))
    def mirror(image):
        # NO CHANGE
        """
        Flip image horizontally (left to right).

        :param image: The image to mirror.
        :return: An image.
        """
        return SizingImage(image.transpose(Image.Transpose.FLIP_LEFT_RIGHT))

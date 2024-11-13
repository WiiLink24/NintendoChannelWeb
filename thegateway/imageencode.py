import io

from PIL import Image, ImageFile


def video_thumbnail_encode(infile: bytes) -> bytes:
    return generic_encode(infile, 96, 72)


def banner_encode(infile: bytes) -> bytes:
    return generic_encode(infile, 128, 48)


def generic_encode(in_bytes: bytes, w: int, h: int) -> bytes:
    """Encodes an image to a format suitable for the Wii."""
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    im = Image.open(io.BytesIO(in_bytes))

    # If we have an alpha channel, it must be removed.
    if im.mode in ("RGBA", "P"):
        im = im.convert("RGB")

    im = im.resize((w, h))

    result = io.BytesIO()
    # These defaults are required for the Wii to read an JPEG.
    im.save(result, "jpeg", subsampling="4:2:0", progressive=False)

    return result.getvalue()

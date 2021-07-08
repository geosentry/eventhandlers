"""
asset-create service

The geotiff module contains functions to handle GeoTIFF assets triggers
"""
from .logentry import LogEntry

def generate_assetname(filename: str) -> str:
    """ A function that returns an asset name for a given filename. """
    try:
        # Split the filename path
        pieces = filename.split("/")
        # Remove the file extension from the last element
        pieces[-1] = pieces[-1].split(".")[0]
        # Join all the elements with a '-' and return it
        return "-".join(pieces)
    
    except Exception as e:
        raise NameError(e)

def convert(filepath: str, outputpath: str):
    """ 
    A function that converts a GeoTIFF image into a PNG or a JPEG image.
    The image is read using the OpenCV2 library and converted to desired format.
    The output format is determined from the file extension of the output path.

    PNG conversion is done with zero compression.
    JPEG conversion is done with a quality value of 200.
    """
    import os
    from cv2 import imread, imwrite
    from cv2 import IMWRITE_PNG_COMPRESSION, IMWRITE_JPEG_QUALITY

    if not os.path.isfile(filepath):
        raise FileNotFoundError("image does not exist")

    imagedata = imread(filepath)

    if outputpath.endswith(".png"):
        imwrite(outputpath, imagedata, [IMWRITE_PNG_COMPRESSION, 0])
    elif outputpath.endswith(".jpg"):
        imwrite(outputpath, imagedata, [IMWRITE_JPEG_QUALITY, 200])
    else:
        raise ValueError("unsupported output type")

def handle_geotiff(filename: str, bucket: str, log: LogEntry):
    """
    A handler function that performs the asset handle runtime for GeoTIFF assets.

    Downloads the asset, converts it into a PNG, reuploads it and then 
    deletes the original GeoTIFF asset from a Cloud Storage Bucket.
    """
    from google.cloud import storage

    log.addtrace("started GeoTIFF asset handler runtime")

    try:
        storage_client = storage.Client()
        bucket_handler = storage_client.bucket(bucket)

    except Exception as e:
        log.addtrace(f"execution broke - could not initialize storage client and bucket handler. {e}")
        return "ALERT", "system error.", "error-acknowledge"

    log.addtrace("storage client and bucket handler initialized.")

    try:
        tmpdir = "/tmp"
        assetname = generate_assetname(filename)
        tmpfile = f"{tmpdir}/{assetname}"

        tifblob = bucket_handler.blob(filename)
        tifblob.download_to_filename(f"{tmpfile}.tiff")

    except NameError as e:
        log.addtrace(f"execution broke - could not generate asset name from filename. {e}")
        return "ERROR", "runtime error.", "error-acknowledge"

    except Exception as e:
        log.addtrace(f"execution broke - could not download GeoTIFF blob. {e}")
        return "ERROR", "runtime error.", "error-acknowledge"

    log.addtrace("GeoTIFF blob downloaded.")

    try:
        convert(f"{tmpfile}.tiff", f"{tmpfile}.png")

    except Exception as e:
        log.addtrace(f"execution broke - could not convert GeoTIFF to PNG. {e}")
        return "ERROR", "runtime error.", "error-acknowledge"

    log.addtrace("GeoTIFF converted to PNG.")

    try:
        outname = filename.split(".")[0] + ".png"

        pngblob = bucket_handler.blob(outname)
        pngblob.upload_from_filename(f"{tmpfile}.png")

    except Exception as e:
        log.addtrace(f"execution broke - could not upload PNG blob. {e}")
        return "ERROR", "runtime error.", "error-acknowledge"

    log.addtrace("PNG blob uploaded.")

    try:
        tifblob.delete()
        
    except Exception as e:
        log.addtrace(f"execution broke - could not delete GeoTIFF blob. {e}")
        return "ERROR", "runtime error.", "error-acknowledge"

    log.addtrace("GeoTIFF blob deleted.")
    log.addtrace("ended GeoTIFF asset handler runtime")
    return "INFO", "GeoTIFF runtime complete", "success-acknowledge"

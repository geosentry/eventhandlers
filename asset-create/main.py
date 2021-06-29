"""
Terrascope Cloud

Google Cloud Platform - Cloud Functions

asset-create service
"""
import os
import cv2
import json
from google.cloud import storage
from google.cloud import firestore

servicename = "asset-create"

def log(severity: str, message: str, trace: list):
    """
    A helper function that logs a given message to Cloud Logging as a structured log 
    given that it is called within a Cloud Run/Function Service. The function accepts 
    a log severity string, a log message string and a a list of trace log strings.

    Accepted log severity values are - EMERGENCY, ALERT, CRITICAL, ERROR, WARNING, NOTICE, INFO, DEBUG and DEFAULT.
    Refer to https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry#logseverity for more information.
    """
    logentry = dict(severity=severity, message=message, trace=trace, service=servicename)
    print(json.dumps(logentry))


def convert(filepath: str, outputname: str) -> bool:
    """ doc """
    if not os.path.isfile(filepath):
        raise FileNotFoundError

    imagedata = cv2.imread(filepath)

    if outputname.endswith(".png"):
        cv2.imwrite(outputname, imagedata, [cv2.IMWRITE_PNG_COMPRESSION, 0])
        return True

    elif outputname.endswith(".jpg"):
        cv2.imwrite(outputname, imagedata, [cv2.IMWRITE_JPEG_QUALITY, 200])
        return True

    return False

def main(event, context):
    """ Cloud Functions Entrypoint """
    logtraces = ["execution started"]

    try:
        bucket = event["bucket"]
        filename = event["name"]
        contenttype = event["contentType"]

        logtraces.append(f"event data read. bucket - {bucket}. filename - {filename}. contenttype - {contenttype}")
        
        if contenttype != "image/tiff":
            logtraces.append("execution terminated - triggered by non GeoTIFF object.")
            log("INFO", "runtime complete.", logtraces)
            return "termination-acknowledge", 200

        logtraces.append("content type checked.")

    except KeyError as e:
        logtraces.append(f"execution broke - could not read event data. missing key {e}")
        log("EMERGENCY", f"system error.", logtraces)
        return "error-acknowledge", 200

    except Exception as e:
        logtraces.append(f"execution broke - could not read event data. {e}")
        log("ERROR", f"runtime error.", logtraces)
        return "error-acknowledge", 200

    try:
        pieces = filename.split("/")
        assettype = pieces[0]

        if assettype == "regions":
            assetpath = f"{pieces[1]}-{pieces[2]}"
            assetname = pieces[3].split(".")[0]
            assetdoc = f"regions/{pieces[1]}/acquisitions/{pieces[2]}"

        elif assettype == "visuals":
            assetpath = pieces[1]
            assetname = pieces[2].split(".")[0]
            assetdoc = f"visuals/{pieces[1]}"

        else: 
            logtraces.append(f"execution terminated - triggered by unsupported asset type {assettype}.")
            log("INFO", "runtime complete.", logtraces)
            return "termination-acknowledge", 200

    except Exception as e:
        logtraces.append(f"execution broke - could not deconstruct object filename. {e}")
        log("ERROR", f"runtime error.", logtraces)
        return "error-acknowledge", 200

    logtraces.append("filename deconstructed.")

    try:
        storage_client = storage.Client()
        bucket_handler = storage_client.bucket(bucket)

    except Exception as e:
        logtraces.append(f"execution broke - could not initialize storage client and bucket handler. {e}")
        log("ALERT", f"system error.", logtraces)
        return "error-acknowledge", 200

    logtraces.append("storage client and bucket handler initialized.")
    
    try:
        tmpdir = "./tmp"
        tmpfile = f"{tmpdir}/{assetpath}-{assetname}"

        tifblob = bucket_handler.blob(filename)
        tifblob.download_to_filename(f"{tmpfile}.tiff")

    except Exception as e:
        logtraces.append(f"execution broke - could not download GeoTIFF blob. {e}")
        log("ERROR", f"runtime error.", logtraces)
        return "error-acknowledge", 200

    logtraces.append("GeoTIFF blob downloaded.")

    try:
        convert(f"{tmpfile}.tiff", f"{tmpfile}.png")

    except Exception as e:
        logtraces.append(f"execution broke - could not convert GeoTIFF to PNG. {e}")
        log("ERROR", f"runtime error.", logtraces)
        return "error-acknowledge", 200

    logtraces.append("GeoTIFF converted to a PNG.")

    try:
        outname = filename.split(".")[0] + ".png"

        pngblob = bucket_handler.blob(outname)
        pngblob.upload_from_filename(f"{tmpfile}.png")

    except Exception as e:
        logtraces.append(f"execution broke - could not upload PNG blob. {e}")
        log("ERROR", f"runtime error.", logtraces)
        return "error-acknowledge", 200

    logtraces.append("PNG blob uploaded.")

    try:
        tifblob.delete()
        logtraces.append("GeoTIFF blob deleted.")

    except Exception as e:
        logtraces.append(f"execution broke - could not delete GeoTIFF blob. {e}")
        log("ERROR", f"runtime error.", logtraces)
        return "error-acknowledge", 200

    try:
        db = firestore.Client()
        
    except Exception as e:
        logtraces.append(f"execution broke - could not initialize firestore client. {e}")
        log("ALERT", f"runtime error.", logtraces)
        return "error-acknowledge", 200

    logtraces.append("firestore client initialized.")

    try:
        # acqdoc update runtime
        # if 

        docref = db.document(assetdoc)
        docsnap = docref.get()

        print(docsnap.exists)


    except Exception as e:
        logtraces.append(f"execution broke - could not initialize firestore client. {e}")
        log("ALERT", f"runtime error.", logtraces)
        return "error-acknowledge", 200





    log("INFO", f"runtime complete.", logtraces)
    return "termination-acknowledge", 200

if __name__ == "__main__":
    event = {
        "bucket": "terrascope-assets",
        "contentType": "image/tiff",
        "name": "regions/testreg/2021-06-24/truecolor.tif"
    }

    main(event, 0)
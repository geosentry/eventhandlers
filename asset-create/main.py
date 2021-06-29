"""
Terrascope Cloud

Google Cloud Platform - Cloud Functions

asset-create service
"""
import json
import assethandler

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

def handle_png(filename: str, logtraces: list):
    from google.cloud import firestore

    logtraces.append("started PNG asset handler")

    try:
        docpath = assethandler.pnglib.generate_assetdoc(filename)
        logtraces.append(f"asset document path generated. docpath - {docpath}")

        db = firestore.Client()
        logtraces.append(f"firestore client initialized")

        docref = db.document(docpath)
        docsnap = docref.get()

        if not docsnap.exists:
            logtraces.append(f"execution broke - could not find asset document on database.")
            return "CRITICAL", "runtime error.", "error-acknowledge", logtraces
            
    except NameError as e:
        logtraces.append(f"execution broke - could not generate asset document path from filename. {e}")
        return "ERROR", "runtime error.", "error-acknowledge", logtraces

    except TypeError as e:
        logtraces.append(f"execution terminated - triggered by unsupported asset type - {e}")
        return "INFO", "runtime terminated.", "termination-acknowledge", logtraces

    except Exception as e:
        logtraces.append(f"execution broke - could not initialize firestore client. {e}")
        return "ALERT", "system error.", "error-acknowledge", logtraces

    logtraces.append(f"asset document path valudated.")

    try:
        assetid = assethandler.pnglib.generate_assetid(filename)
        
        #TODO - define asset path and check update runtime
        docref.set({f"assets.path.{assetid}": filename}, merge=True)

    except NameError as e:
        logtraces.append(f"execution broke - could not generate asset ID from filename. {e}")
        return "ERROR", "runtime error.", "error-acknowledge", logtraces
        
    except Exception as e:
        logtraces.append(f"execution broke - could not update asset document. {e}")
        return "ALERT", "system error.", "error-acknowledge", logtraces
    
    logtraces.append(f"asset document updated")

    # check if all document assets have been generated.
    # send pubsub trigger to pdf-builds if true


def main(event, context):
    """ Cloud Functions Entrypoint """
    logtraces = ["execution started"]

    try:
        bucket = event["bucket"]
        filename = event["name"]
        contenttype = event["contentType"]

        logtraces.append(f"event data read. bucket - {bucket}. filename - {filename}.")
    
    except KeyError as e:
        logtraces.append(f"execution broke - could not read event data. missing key {e}")
        log("EMERGENCY", f"system error.", logtraces)
        return "error-acknowledge", 200

    try:
        if contenttype == "image/tiff":
            severity, message, response, logtraces = assethandler.tiflib.handle_geotiff(filename, bucket, logtraces)

            logtraces.append("execution complete")
            log(severity, message, logtraces)
            return response, 200

        elif contenttype == "image/png":
            return "", 200
        
        else:
            logtraces.append(f"execution terminated - triggered by unsupported object of type - {contenttype}.")
            log("INFO", "runtime terminated.", logtraces)
            return "termination-acknowledge", 200

    except Exception as e:
        logtraces.append(f"execution broke - could not run {contenttype} runtime. {e}")
        log("ERROR", f"runtime error.", logtraces)
        return "error-acknowledge", 200



if __name__ == "__main__":
    event = {
        "bucket": "terrascope-assets",
        "contentType": "image/tiff",
        "name": "regions/testreg/2021-06-24/truecolor.tif"
    }

    main(event, 0)

"""
Terrascope Cloud

Google Cloud Platform - Cloud Functions

acquisition-builder service
"""
import ee
import json
import base64
import geocore
import google.cloud.firestore as firestore

servicename = "acquisition-builder"

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

def parse_pubsub_event(event: dict):
    """ 
    A helper function that parses and decodes a PubsubMessage event dictionary 
    and returns the data and message attributes from it.
    
    The event dictionary must follow the PubsubMessage REST Specification. 
    Refer to https://cloud.google.com/pubsub/docs/reference/rest/v1/PubsubMessage.
    """
    if not isinstance(event, dict):
        raise TypeError("event is not a dictionary")

    if 'data' not in event:
        raise ValueError("event does not contain 'data'")

    if 'attributes' not in event:
        raise ValueError("event does not contain 'attributes'")

    try:
        data = base64.b64decode(event['data']).decode('utf-8')
        attributes = event['attributes']

    except Exception as e:
        raise UnicodeError(f"event data could not be decoded as a base64 string - {e}")

    return data, attributes


def main(event, context):
    """ Cloud Functions Entrypoint """
    logtraces = ["execution started."]

    try:
        docpath, _ = parse_pubsub_event(event)

    except Exception as e:
        logtraces.append(f"execution broke - could not read pubsub event data. {e}")
        log("EMERGENCY", f"system error.", logtraces)
        return "error-acknowldege", 200

    logtraces.append(f"event data read. document - {docpath}.")

    try:
        db = firestore.Client()
        logtraces.append(f"firestore client initialized.")

        geocore.initialize(db.project)
        logtraces.append(f"earth engine session initialized.")
        
    except RuntimeError as e:
        logtraces.append(f"execution broke - could not initialize earth engine session. {e}")
        log("ALERT", f"system error.", logtraces)
        return "error-acknowledge", 200

    except Exception as e:
        logtraces.append(f"execution broke - could not initialize firestore client. {e}")
        log("ALERT", f"system error.", logtraces)
        return "error-acknowledge", 200

    try:
        docref = db.document(docpath)
        docdata = docref.get().to_dict()

        logtraces.append(f"region document data retrieved.")

        geojson = docdata["geojson"]
        geometry = geocore.spatial.generate_geometry(geojson)

    except KeyError:
        logtraces.append(f"execution broke - could not read geojson field from region document.")
        log("ERROR", f"runtime error.", logtraces)
        return "error-acknowledge", 200

    except RuntimeError as e:
        logtraces.append(f"execution broke - could not generate geometry from region geojson. {e}")
        log("ERROR", f"runtime error.", logtraces)
        return "error-acknowledge", 200

    except Exception as e:
        logtraces.append(f"execution broke - could not retrieve region document data from firestore. {e}")
        log("ERROR", f"runtime error.", logtraces)
        return "error-acknowledge", 200

    logtraces.append(f"region geometry generated.")

    try:
        acqdate = docdata.get("next_acquisition")
        if not acqdate:
            acqdate = geocore.acquisition.generate_latest_date(geometry)
            logtraces.append(f"new region. acquisition date generated.")
        else:
            acqdate = geocore.temporal.generate_date_googledate(acqdate)

        logtraces.append(f"acquisition date determined. date - {acqdate.isoformat()}")

        acqimage = geocore.acquisition.generate_latest_image(acqdate, geometry)
        if not acqimage:
            logtraces.append(f"execution terminated - region has no available acquisitions.")
            log("INFO", "runtime terminated.", logtraces)
            return "termination-acknowledge", 200

        logtraces.append(f"acquisition image found")

        acqimageid = geocore.acquisition.generate_image_identifier(acqimage)
        logtraces.append(f"acquisition image ID retrieved. imageID - {acqimageid}.")

    except Exception as e:
        logtraces.append(f"execution broke - could not find latest acquisition for region. {e}")
        log("ERROR", f"runtime error.", logtraces)
        return "error-acknowledge", 200

    try:
        nextacq = geocore.temporal.generate_date_nextacquisition(acqdate)
        docref.set({
            "next_acquisition": geocore.temporal.generate_googledate_date(nextacq),
            "last_acquisition": geocore.temporal.generate_googledate_date(acqdate),
        }, merge=True)

    except Exception as e:
        logtraces.append(f"execution broke - could not update region document. {e}")
        log("CRITICAL", f"runtime error.", logtraces)
        return "error-acknowledge", 200

    logtraces.append(f"region document updated.")

    # CLOUD PROBABILITY DETECTION RUNTIME

    try:
        assets = ["truecolor", "ndvi"]
        tcimage = geocore.spectral.generate_TrueColor(acqimage).clip(geometry)
        ndviimage = geocore.spectral.generate_NDVI(acqimage).clip(geometry)

    except Exception as e:
        logtraces.append(f"execution broke - could not generate acquisition asset images. {e}")
        log("ERROR", f"runtime error.", logtraces)
        return "error-acknowledge", 200

    logtraces.append(f"asset images generated.")

    try:
        acqID = acqdate.isoformat().split("T")[0]
        logtraces.append(f"acquisition ID generated. acquistion ID - {acqID}")
        
        # export runtime (temporary) - needs to accomodate a variable number of generations
        tcexport = geocore.export.export_image_asset(tcimage, geometry, f"{docpath}/{acqID}/truecolor")
        tcexport.start()

        ndviexport = geocore.export.export_image_asset(ndviimage, geometry, f"{docpath}/{acqID}/ndvi")
        ndviexport.start()

    except ee.EEException as e:
        logtraces.append(f"execution broke - could not export asset images. earth engine error. {e}")
        log("CRITICAL", f"runtime error.", logtraces)
        return "error-acknowledge", 200

    except Exception as e:
        logtraces.append(f"execution broke - could not export asset images. runtime error. {e}")
        log("ERROR", f"runtime error.", logtraces)
        return "error-acknowledge", 200

    logtraces.append(f"asset images exported.")

    try:
        acqdoc = docref.collection("acquisitions").document(acqID)
        acqdoc.set({
            "image": acqimageid,
            "timestamp": geocore.temporal.generate_googledate_date(acqdate),
            "subscription": "farm-analytics",
            "asset-bucket": "terrascope-assets",
            "asset-paths": {key: None for key in assets},
            "report-bucket": "terrascope-reports",
            "report-path": None,       
        })

    except Exception as e:
        logtraces.append(f"execution broke - could not create acquisition document. {e}")
        log("CRITICAL", f"runtime error.", logtraces)
        return "error-acknowledge", 200
    
    logtraces.append("execution complete.")
    log("INFO", f"runtime complete.", logtraces)
    return "success-acknowledge", 200

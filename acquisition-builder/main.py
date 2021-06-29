"""
Terrascope Cloud

Google Cloud Platform
Cloud Functions

function: acquisition-builder
runtime: python39
trigger-topic: acquisition-builds
service-account permissions:
- Secret Accesor
- Cloud Datastore User
"""
import ee
import json
import base64
import geocore
import google.cloud.firestore as firestore

def log(severity: str, message: str, metadata: dict):
    """
    A helper function that logs a given message to Cloud Logging as a structured log 
    given that it is called within a Cloud Run/Function Service. The function accepts 
    a log severity string, a log message string and a log metadata dictionary.

    Accepted log severity values are - EMERGENCY, ALERT, CRITICAL, ERROR, WARNING, NOTICE, INFO, DEBUG and DEFAULT.
    Refer to https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry#logseverity for more information.
    """
    logentry = dict(severity=severity, message=message, **metadata)
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
    logmetadata = {"service": "acquisition-builder"}

    try:
        docpath, _ = parse_pubsub_event(event)

    except Exception as e:
        log("EMERGENCY", f"failed to parse pubsub event data. {e}", logmetadata)
        return "error-acknowldege", 200

    logmetadata.update({"document-path": docpath})

    try:
        db = firestore.Client()
        geocore.initialize(db.project)
        
    except RuntimeError as e:
        log("ALERT", f"failed to setup cloud clients. {e}.", logmetadata)
        return "error-acknowledge", 200
    except Exception as e:
        log("ALERT", f"failed to setup cloud clients. unable to initialize a firestore client. {e}.", logmetadata)
        return "error-acknowledge", 200

    logmetadata.update({"gcp-project": db.project})

    try:
        docref = db.document(docpath)
        docdata = docref.get().to_dict()

        active = docdata["active"]
        geojson = docdata["geojson"]

        if not active:
            log("INFO", "region has been deactivated", logmetadata)
            return "termination-acknowledge", 200

    except KeyError as e:
        log("CRITICAL", f"failed to read region document data. missing key {e}")
        return "error-acknowledge", 200
    except Exception as e:
        log("ALERT", f"failed to read region document data. {e}.", logmetadata)
        return "error-acknowledge", 200

    try:
        geometry = geocore.spatial.generate_geometry(geojson)
        acqdate = docdata.get("next_acquisition")

        if not acqdate:
            acqdate = geocore.acquisition.generate_latest_date(geometry)
        else:
            acqdate = geocore.temporal.generate_date_googledate(acqdate)

        acqimage = geocore.acquisition.generate_latest_image(acqdate, geometry)

        if not acqimage:
            log("INFO", "region has no available acquisitions", logmetadata)
            return "termination-acknowledge", 200

        acqimageid = geocore.acquisition.generate_image_identifier(acqimage)

    except Exception as e:
        log("ALERT", f"failed to find latest acquisition for the region. {e}.", logmetadata)
        return "error-acknowledge", 200

    try:
        nextacq = geocore.temporal.generate_date_nextacquisition(acqdate)
        docref.set({
            "next_acquisition": geocore.temporal.generate_googledate_date(nextacq),
            "last_acquisition": geocore.temporal.generate_googledate_date(acqdate),
        }, merge=True)

    except Exception as e:
        log("ALERT", f"failed to update the region document. {e}.", logmetadata)
        return "error-acknowledge", 200

    # CLOUD PROBABILITY DETECTION RUNTIME

    try:
        tcimage = geocore.spectral.generate_TrueColor(acqimage).clip(geometry)
        ndviimage = geocore.spectral.generate_NDVI(acqimage).clip(geometry)

    except Exception as e:
        log("ALERT", f"failed to generate acquisition asset images. {e}.", logmetadata)
        return "error-acknowledge", 200

    try:
        acqID = acqdate.isoformat().split("T")[0]
        assets = ["truecolor", "ndvi"]
        assetpaths = {key: f"{docpath}/{acqID}/{key}" for key in assets}

        # export runtime (temporary) - needs to accomodate a variable number of generations
        tcexport = geocore.export.export_image_asset(tcimage, geometry, assetpaths["truecolor"])
        tcexport.start()

        ndviexport = geocore.export.export_image_asset(ndviimage, geometry, assetpaths["ndvi"])
        ndviexport.start()

    except ee.EEException as e:
        log("ALERT", f"failed to export acquisition asset images. earth engine error. {e}.", logmetadata)
        return "error-acknowledge", 200
    except Exception as e:
        log("ALERT", f"failed to export acquisition asset images. runtime error. {e}.", logmetadata)
        return "error-acknowledge", 200

    try:
        acqdoc = docref.collection("acquisitions").document(acqID)
        acqdoc.set({
            "image": acqimageid,
            "timestamp": geocore.temporal.generate_googledate_date(acqdate),
            "subscription": "farm-analytics",
            "asset": {
                "bucket": "terrascope-assets",
                "completion": {key: False for key in assets},
                "path": assetpaths
            },
            "report": {
                "bucket": "terrascope-reports",
                "completion": False,
                "path": "regions/regid/acqid.pdf"
            }            
        })

    except Exception as e:
        log("ALERT", f"failed to create acquisition document. {e}.", logmetadata)
        return "error-acknowledge", 200
    
    log("INFO", f"completed acquisition-builder runtime.", logmetadata)
    return "success-acknowledge", 200

if __name__ == "__main__":
    event = {
        "data": base64.b64encode("regions/testreg".encode("utf-8")),
        "attributes": {}
    }

    main(event, 0)
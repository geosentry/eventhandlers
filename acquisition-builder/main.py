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
import json
import base64
import geocore
import google.cloud.firestore as firestore
from google.api_core.datetime_helpers import DatetimeWithNanoseconds


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
    logmetadata = {"service": "acquisition-builder", "event": event}

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
            acqdate = geocore.acquisition.generate_latest_date()

        latest_acq = geocore.acquisition.generate_latest_image(acqdate, geometry)
        imageid = geocore.acquisition.generate_image_identifier(latest_acq)

    except Exception as e:
        log("ALERT", f"failed to find latest acquisition for the region. {e}.", logmetadata)
        return "error-acknowledge", 200

    try:
        newlast = DatetimeWithNanoseconds.fromisoformat(acqdate.isoformat())
        newnext = geocore.temporal.generate_date_nextacquisition(acqdate)
        newnext = DatetimeWithNanoseconds.fromisoformat(newnext.isoformat())

        docref.set({
            "next_acquisition": newnext,
            "last_acquisition": newlast,
            "temp_imageid": imageid,
        }, merge=True)

    except Exception as e:
        log("ALERT", f"failed to update the acquisition document. {e}.", logmetadata)
        return "error-acknowledge", 200

    log("INFO", f"completed acquisition-builder runtime.", logmetadata)
    return "success-acknowledge", 200

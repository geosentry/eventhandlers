"""
Terrascope Cloud

service: region-create
runtime: Python 3.9
environment: Cloud Functions

trigger-event: providers/cloud.firestore/eventTypes/document.create 
trigger-resource: projects/{projectID}/databases/(default)/documents/regions/{regionID}
"""
import json

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


def main(event, context):
    """doc"""
    logmetadata = {"service": "region-event", "event": event}

    try:
        regiondoc = event['value']['name']
        regiondoc = regiondoc.split('documents/')[-1]
        docfields = event['value']['fields']

    except KeyError as e:
        log("EMERGENCY", f"failed to parse event data: missing key - '{e}'", logmetadata)
        return "Failure", 200
    except Exception as e:
        log("ERROR", f"failed to parse event data: {e}", logmetadata)
        return "Failure", 200

    logmetadata.update({"document-path": regiondoc})

    log("NOTICE", f"completed", logmetadata)
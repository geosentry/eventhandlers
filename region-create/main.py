"""
Terrascope Cloud

Google Cloud Platform
Cloud Functions

function: region-create
runtime: python39
trigger-event: providers/cloud.firestore/eventTypes/document.create 
trigger-resource: projects/{projectID}/databases/(default)/documents/regions/{regionID}
service-account permissions:
- Pub/Sub Publisher
"""
import json
import google.cloud.pubsub

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
    """ Runtime Entrypoint """
    logmetadata = {"service": "region-create", "event": event}

    try:
        regiondoc = event['value']['name']
        gcpproject = regiondoc.split("/")[1]
        regiondoc = regiondoc.split('documents/')[-1]

    except KeyError as e:
        log("EMERGENCY", f"failed to parse event data. missing key - '{e}'", logmetadata)
        return "error-acknowledge", 200
    except Exception as e:
        log("ALERT", f"failed to parse event data. {e}", logmetadata)
        return "error-acknowldege", 200

    logmetadata.update({"document-path": regiondoc, "gcp-project": gcpproject})

    try:
        publisher = google.cloud.pubsub.PublisherClient()
        message = regiondoc.encode('utf-8')
        
    except Exception as e:
        log("ALERT", f"failed to setup cloud pubsub client and topics. {e}.", logmetadata)
        return "error-acknowledge", 200

    try:
        emailtopic = f'projects/{gcpproject}/topics/email-builds'
        publisher.publish(topic=emailtopic, data=message, runtime="new-region")
        
    except Exception as e:
        log("ALERT", f"failed to trigger the 'new-region' email-build. {e}.", logmetadata)
    else:
        log("DEBUG", f"succesfully triggered 'new-region' email-build.", logmetadata)

    try:
        acqtopic = f'projects/{gcpproject}/topics/acquisition-builds'
        publisher.publish(topic=acqtopic, data=message)

    except Exception as e:
        log("ALERT", f"failed to trigger the acquisition-build. {e}.", logmetadata)
        return "error-acknowledge", 200
    else:
        log("DEBUG", f"succesfully triggered the acquisition-build.", logmetadata)

    log("INFO", f"completed region-create runtime.", logmetadata)
    return "success-acknowledge", 200

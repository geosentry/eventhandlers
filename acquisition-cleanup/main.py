"""
Terrascope Cloud

service: acquisition-cleanup
runtime: Python 3.9
environment: Cloud Functions

trigger-topic: cleanups
"""
import json
import base64

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

def parse(event: dict):
    """ 
    A helper function that parses and decodes a PubsubMessage event dictionary 
    and returns the data and message attributes from it.
    
    The event dictionary must follow the PubsubMessage REST Specification. 
    Refer to https://cloud.google.com/pubsub/docs/reference/rest/v1/PubsubMessage.
    """
    if not isinstance(event, dict):
        raise ValueError("event is not a dictionary")

    if 'message' not in event:
        raise ValueError("event does not contain 'message'")

    message = event['message']

    if 'data' not in message:
        raise ValueError("event message does not contain 'data'")

    if 'attributes' not in message:
        raise ValueError("event message does not contain 'attributes'")

    try:
        data = base64.b64decode(message['data']).decode('utf-8')
        attributes = message['attributes']

    except Exception as e:
        raise UnicodeError(f"event message data, base64 decode failed: {e}")

    return data, attributes
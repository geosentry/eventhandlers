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


def main(event, context):
    """ Cloud Functions Entrypoint """
    logtraces = ["execution started"]

    try:
        bucket = event["bucket"]
        filename = event["name"]
        contenttype = event["contentType"]
    
    except KeyError as e:
        logtraces.append(f"execution broke - could not read bucket event data. missing key {e}")
        log("EMERGENCY", f"system error.", logtraces)
        return "error-acknowledge", 200

    logtraces.append(f"event data read. bucket - {bucket}. filename - {filename}.")

    try:
        if contenttype == "image/tiff":
            severity, message, response, logtraces = assethandler.tiflib.handle_geotiff(filename, bucket, logtraces)

            logtraces.append("execution complete")
            log(severity, message, logtraces)
            return response, 200

        elif contenttype == "image/png":
            severity, message, response, logtraces = assethandler.pnglib.handle_png(filename, logtraces)

            logtraces.append("execution complete")
            log(severity, message, logtraces)
            return response, 200
        
        else:
            logtraces.append(f"execution terminated - triggered by unsupported object of type - {contenttype}.")
            log("INFO", "runtime terminated.", logtraces)
            return "termination-acknowledge", 200

    except Exception as e:
        logtraces.append(f"execution broke - could not run {contenttype} runtime. {e}")
        log("ERROR", f"runtime error.", logtraces)
        return "error-acknowledge", 200

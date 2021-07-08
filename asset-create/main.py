"""
GeoSentry Event Handler

Google Cloud Platform - Cloud Functions

asset-create service
"""
from pkg.logentry import LogEntry

def main(event, context):
    """ Cloud Functions Entrypoint """
    log = LogEntry()

    try:
        bucket = event["bucket"]
        filename = event["name"]
        contenttype = event["contentType"]
    
    except KeyError as e:
        log.addtrace(f"execution broke - could not read bucket event data. missing key {e}")
        log.flush("EMERGENCY", f"system error.")
        return "error-acknowledge", 200

    log.addtrace(f"event data read. bucket - {bucket}. filename - {filename}.")

    try:
        if contenttype == "image/tiff":
            from pkg.geotiff import handle_geotiff

            severity, message, response = handle_geotiff(filename, bucket, log)

            log.flush(severity, message)
            return response, 200

        elif contenttype == "image/png":
            from pkg.png import handle_png

            severity, message, response = handle_png(filename, log)

            log.flush(severity, message)
            return response, 200
        
        else:
            log.addtrace(f"execution terminated - triggered by unsupported object of type - {contenttype}.")
            log("INFO", "runtime terminated.")
            return "termination-acknowledge", 200

    except Exception as e:
        log.addtrace(f"execution broke - could not run {contenttype} runtime. {e}")
        log("ERROR", f"runtime error.")
        return "error-acknowledge", 200

if __name__ == "__main__":
    event = {
        "bucket": "geosentry-assets",
        "contentType": "image/tiff",
        "name": "regions/testreg/2021-06-24/truecolor.tif"
    }

    main(event, 0)
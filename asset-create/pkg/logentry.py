"""
asset-create service

The logentry module implements the LogEntry class.
"""

class LogEntry:
    """ A class that represents a serverless log compliant with Google Cloud Platform. """

    service = "asset-create"

    def __init__(self) -> None:
        """ Initialization Method """
        self.logtrace: list = [f"execution started."]

        self.baselog = {
            "trace": self.logtrace, 
            "service":self.service
        }

    def addtrace(self, trace: str):
        """ A method that adds a trace string to the list of logtraces. """
        self.logtrace.append(trace)

    def flush(self, severity: str, message: str):
        """
        A method of LogEntry that creates and flushes the built log to Cloud Logging as
        a structured log given that it is called within a Cloud Run/Functions Service.
        The method accepts a log severity string and a log message string.

        Accepted log severity values are - EMERGENCY, ALERT, CRITICAL, ERROR, WARNING, NOTICE, INFO, DEBUG and DEFAULT.
        Refer to https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry#logseverity for more information.
        """
        import json

        self.addtrace("execution ended.")
        logentry = dict(severity=severity, message=message)
        logentry.update(self.baselog)

        print(json.dumps(logentry))

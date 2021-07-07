package function

import (
	"encoding/json"
	"fmt"
)

/*
A structure that represents a serverless
log compliant with Google Cloud Platform.
*/
type LogEntry struct {
	Message  string   `json:"message"`
	Severity string   `json:"severity"`
	Service  string   `json:"service"`
	Trace    []string `json:"trace"`
}

// A constructor function that generates a base LogEntry and returns it.
func NewLogEntry() *LogEntry {
	// Create a new logentry object
	log := LogEntry{Service: "acquisition-create", Trace: []string{"execution started"}}
	// Return the new logentry object
	return &log
}

// A method of LogEntry that adds a string to the log traces.
func (log *LogEntry) addtrace(tracestr string) {
	// Append the trace string to the
	log.Trace = append(log.Trace, tracestr)
}

/*
A method of LogEntry that creates and flushes the built log to Cloud Logging as
a structured log given that it is called within a Cloud Run/Functions Service.
The method accepts a log severity string and a log message string.

Accepted log severity values are - EMERGENCY, ALERT, CRITICAL, ERROR, WARNING, NOTICE, INFO, DEBUG and DEFAULT.
Refer to https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry#logseverity for more information.
*/
func (log *LogEntry) flush(severity string, message string) {
	// Add an execution end trace
	log.addtrace("execution ended")

	// Check Severity value and set it
	switch severity {
	case "EMERGENCY", "ALERT", "CRITICAL", "ERROR", "WARNING", "NOTICE", "INFO", "DEBUG", "DEFAULT":
		log.Severity = severity
	default:
		log.Severity = "DEFAULT"
	}

	// Set the log message
	log.Message = message

	// Marshal the logentry into a slice of bytes
	out, _ := json.Marshal(log)
	// Cast the byte slice into a string and flush to stdout
	fmt.Println(string(out))
}

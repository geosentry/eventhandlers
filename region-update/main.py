"""
Terrascope Cloud

service: region-update
runtime: Python 3.9
environment: Cloud Functions

trigger-event: providers/cloud.firestore/eventTypes/document.update 
trigger-resource: projects/{projectID}/databases/(default)/documents/regions/{regionID}
"""
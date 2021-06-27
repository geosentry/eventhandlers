"""
Terrascope Cloud

service: acquisition-delete
runtime: Python 3.9
environment: Cloud Functions

trigger-event: providers/cloud.firestore/eventTypes/document.delete 
trigger-resource: projects/{projectID}/databases/(default)/documents/regions/{regionID}/acquisitions/{acquistionID}
"""
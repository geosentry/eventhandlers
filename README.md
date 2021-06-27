# Terrascope
A geospatial data subscription service that sends spectral analytics and stunning visuals powered by Google Earth Engine to your email regularly.

!todo - add link to deployed project

## In Development
**Version: 0.1.0**  
**Platform: Google Cloud Platform**  
**Language: Python 3.9**  
**License: MIT**

## Overview
- High level overview of Terrascope

### Project Structure
- Directory structure

### Dependancies 
- Google Earth Engine
- Google Cloud Client Libraries
- FDPF2 and Email Tool(?)
- Flask, GUnicorn and Docker

### System Design and Cloud Architecture
- System Diagram
- Low level overview

## Google Earth Engine
- High level overview of Google Earth Engine
- Data Catalog
- Website

### Earth Engine 101
- Client v Server
- Deferred Execution
- Python API
- Authentication
- Exports
- Visualization

### Earth Engine + Terrascope
- GeoCore Library
- Sentinel-2 MSI
- Cloud Probability
- Area Equalization and Tesselation
- Spectral Indices, Scene Classifcation, False Composites
- Analytics Engine
- Visuals Engine
- Acquistion Checker Runtime

## Google Cloud Platform & Serverless
- High level overview of GCP

### Serverless Compute
- Cloud Run
- Cloud Functions

### Serverless Data Storage
- Cloud Storage
- Cloud Firestore

### Serverless Events
- Cloud Pub/Sub
https://cloud.google.com/pubsub/docs/reference/rest/v1/PubsubMessage
- Cloud Scheduler
- Cloud Events (EventArc)

### Serverless Logging
- **Serverless Container Log Writing Guide**: https://cloud.google.com/run/docs/logging#container-logs
- **Log Severity Strings**: https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry#logseverity
- **LogEntry Structure**: https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry

### CI/CD
- Github Actions
- Cloud Build
- Docker

## PDF Generation
- FPDF2
- pdfgen lib

## Email Notifications
- ?
- emailgen lib

## Front-End Interface
- link to external repository
# region-reshape

### Runtime
Platform: **Google Cloud Platform**  
Environment: **Cloud Functions**
Runtime: **python39** (Python 3.9)  

### Trigger
Trigger Type: **HTTP**  

### Function Flow  
!todo  
When a HTTP request is recieved, parse the request for a GeoJSON and reshape it according to the following spec,
- If GeoJSON is a point geometry, construct a bounding circle with a 500m radius and reshape into a bounding square.
- If GeoJSON is a linestring geomerty, construct a bounding circle with the line centroid and radius based on line extent from centroid and then reshape into a bounding square.
- If GeoJSON is a polygon, construct a bounding circle and reshape into a bounding square.
- If GeoJSON is a multi-polygon or multi-linestring, simplify into a single feature and reshape.

### Deployment
All pushes to this directory automatically trigger a workflow to deploy the Cloud Function to a GCP Project.   
The GitHub Actions workflow is defined in the ``.github/workflows/deploy-region-reshape.yml`` file.

The command used to deploy the function is as follows
```bash
gcloud functions deploy region-reshape \
--region $REGION \
--service-account $SAEMAIL \
--runtime python39 \
--entry-point main \
--trigger-http
```
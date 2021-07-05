# region-create

### Runtime
Platform: **Google Cloud Platform**  
Environment: **Cloud Functions**
Runtime: **go113** (Go 1.13)  

### Trigger
Trigger Type: **Firestore**  
Trigger Event: **providers/cloud.firestore/eventTypes/document.create**
Trigger Resource: **regions/{region}**  

### Service Account Permissions
- **PubSub Publisher** (Cloud Pub/Sub)  
- **Cloud Datastore User** (Firestore)
- **Cloud Function Invoker** (Cloud Functions)

### Function Flow  
!todo  
When a region document is created, make a HTTP call to an function that reshapes the GeoJSON string into a bounding box square. 
Verify the subscription parameters and fallback to defaults if the dont exist.Update the 'geojson' field of the document and then publish either of the folllwing triggers to taskbuilds topic based on the type of region. 
- If vis region, send a visbuild trigger.
- If acq region, send a topobuild and an nltxbuild trigger along with 5 acqbuild triggers for each of the last 5 acquisition dates. 

### Deployment
All pushes to this directory automatically trigger a workflow to deploy the Cloud Function to a GCP Project.   
The GitHub Actions workflow is defined in the ``.github/workflows/deploy-region-create.yml`` file.

The command used to deploy the function is as follows
```bash
gcloud functions deploy region-create \
--region $REGION \
--service-account $SAEMAIL \
--runtime go113 \
--entry-point Main \
--trigger-event providers/cloud.firestore/eventTypes/document.create
--trigger-resource projects/$PROJECTID/databases/(default)/documents/regions/{region}
```
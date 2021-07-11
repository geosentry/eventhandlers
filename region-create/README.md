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
1. Create the function runner, setup its execution and start the logger.
2. Setup the Firestore Client and the Document Reference for the *region* document.
3. Resolve the GeoCorce Service APIs and obtain the URLs for the **Reshape** and **Geocode** APIs.
4. Make HTTP requests to **Reshape** and **Geocode** APIs. Update the *region* document.
4. Setup the PubSub Client, Topic Handler and Build Message. 
5. Publish a message to the **taskbuilds** topic based on the *region* document type. The messsage contains the document path of the document and the 'runtime' attribute is
    - *new-vis-region* for 'vis-region' type.
    - *new-acq-region* for 'acq-region' type.
6. Confirm the success of the publish and log the publish ID.

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
--set-env-vars GCP_PROJECT=$PROJECTID,GCP_REGION=$REGION
```
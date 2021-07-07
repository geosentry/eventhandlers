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
1. Obtain the path to the *region* document and the GCP project ID by parsing the event dictionary from the Firestore trigger.
2. (TODO) Read the 'geojson' field of the *region* document and make a HTTP request to the GeoCore API's **/reshape** endpoint.
3. (TODO) Update the 'geojson' field of the *region* document with the new reshaped GeoJSON data.
4. Initialize the PubSub Client and Topic Handler.
5. Determine the type of the *region* document from it's 'type' field.
6. Publish a message to the **taskbuilds** topic based on the *region* document type. The messsage contains the document path of the document and the 'runtime' attribute is
    - *new-vis-region* for 'vis-region' type.
    - *new-acq-region* for 'user-region' type.
7. Confirm the success of the publish and log the publish ID.

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
# acquisition-create

### Runtime
Platform: **Google Cloud Platform**  
Environment: **Cloud Functions**
Runtime: **go113** (Go 1.13)  

### Trigger
Trigger Type: **Firestore**  
Trigger Event: **providers/cloud.firestore/eventTypes/document.create**
Trigger Resource: **regions/{region}/acquisitions/{acquisition}**  

### Service Account Permissions
- **PubSub Publisher** (Cloud Pub/Sub)  
- **Cloud Datastore User** (Firestore)

### Function Flow  
!todo  
When an acquisition document is created, update the corresponding region document's 'availiable_acqs' array of DocumentReferences by removing the first and adding the acquisition reference to the end of the array. Set the removed acquisition document's 'active' bool to false to flag it for cleanup.  

### Deployment
All pushes to this directory automatically trigger a workflow to deploy the Cloud Function to a GCP Project.   
The GitHub Actions workflow is defined in the ``.github/workflows/deploy-acquisition-create.yml`` file.

The command used to deploy the function is as follows
```bash
gcloud functions deploy acquisition-create \
--region $REGION \
--service-account $SAEMAIL \
--runtime go113 \
--entry-point Main \
--trigger-event providers/cloud.firestore/eventTypes/document.create
--trigger-resource projects/$PROJECTID/databases/(default)/documents/regions/{region}/acquisitions/{acquisition}
```
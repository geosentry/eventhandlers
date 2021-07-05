# acquisition-delete

### Runtime
Platform: **Google Cloud Platform**  
Environment: **Cloud Functions**
Runtime: **go113** (Go 1.13)  

### Trigger
Trigger Type: **Firestore**  
Trigger Event: **providers/cloud.firestore/eventTypes/document.delete**
Trigger Resource: **regions/{region}/acquisitions/{acquisition}**  

### Service Account Permissions
- **Storage Object Admin** (Cloud Storage)  

### Function Flow  
!todo  
When an acquisition document is deleted, delete the corresponding assets from the cloud storage bucket 

### Deployment
All pushes to this directory automatically trigger a workflow to deploy the Cloud Function to a GCP Project.   
The GitHub Actions workflow is defined in the ``.github/workflows/deploy-acquisition-delete.yml`` file.

The command used to deploy the function is as follows
```bash
gcloud functions deploy acquisition-delete \
--region $REGION \
--service-account $SAEMAIL \
--runtime go113 \
--entry-point Main \
--trigger-event providers/cloud.firestore/eventTypes/document.delete
--trigger-resource projects/$PROJECTID/databases/(default)/documents/regions/{region}/acquisitions/{acquisition}
```
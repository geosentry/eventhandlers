# user-delete

### Runtime
Platform: **Google Cloud Platform**  
Environment: **Cloud Functions**
Runtime: **go113** (Go 1.13)  

### Trigger
Trigger Type: **Firebase Authentication**  
Trigger Event: **providers/firebase.auth/eventTypes/user.delete**
Trigger Resouce: Project ID

### Service Account Permissions
- **Cloud Datastore User** (Firestore)

### Function Flow  
!todo  
When a user is deleted, read the corresponding regions from the user document and and delete each of them along with the user document itself.

### Deployment
All pushes to this directory automatically trigger a workflow to deploy the Cloud Function to a GCP Project.   
The GitHub Actions workflow is defined in the ``.github/workflows/deploy-user-create.yml`` file.

The command used to deploy the function is as follows
```bash
gcloud functions deploy user-create \
--region $REGION \
--service-account $SAEMAIL \
--runtime go113 \
--entry-point Main \
--trigger-event providers/firebase.auth/eventTypes/user.create \
--trigger-resource $PROJECTID
```
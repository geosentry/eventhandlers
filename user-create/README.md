# user-create

### Runtime
Platform: **Google Cloud Platform**  
Environment: **Cloud Functions**
Runtime: **go113** (Go 1.13)  

### Trigger
Trigger Type: **Firebase Authentication**  
Trigger Event: **providers/firebase.auth/eventTypes/user.create**
Trigger Resouce: Project ID

### Service Account Permissions
- **Cloud Datastore User** (Firestore)

### Function Flow  
!todo  
When a new user is created, create a corresponding user document with the UID in the 'users' collection of Firestore.

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
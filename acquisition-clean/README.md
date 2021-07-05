# acquisition-clean

### Runtime
Platform: **Google Cloud Platform**  
Environment: **Cloud Functions**
Runtime: **go113** (Go 1.13)  

### Trigger
Trigger Type: **PubSub**  
Trigger Topic: **cleanups**  

### Service Account Permissions
- **Cloud Datastore User** (Firestore)

### Function Flow  
!todo  
When an pubsub message is recieved,
1. Query the **acquisitions** collection group for documents that have the active field set to false.
2. Delete all the documents in the query result.
3. Query the **visuals** collection group for document that have the approved field set to false.
4. Delete all the document in the query result.

### Deployment
All pushes to this directory automatically trigger a workflow to deploy the Cloud Function to a GCP Project.   
The GitHub Actions workflow is defined in the ``.github/workflows/deploy-acquisition-clean.yml`` file.

The command used to deploy the function is as follows
```bash
gcloud functions deploy acquisition-clean \
--region $REGION \
--service-account $SAEMAIL \
--entry-point Main \
--runtime go113 \
--trigger-topic cleanups 
```
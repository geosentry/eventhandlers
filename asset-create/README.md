# asset-create

### Runtime
Platform: **Google Cloud Platform**  
Environment: **Cloud Functions**
Runtime: **python39** (Python 3.9)  

### Trigger
Trigger Type: **Cloud Storage Create**  
Trigger Bucket: **terrascope-assets**  

### Service Account Permissions
Default Credentials
- **Cloud Datastore User** (Firestore)
- **Pub/Sub Publisher** (Cloud PubSub)


### Function Flow
1.
2. 

todo
- This cloud function is responsible for handling object creation events for the **terrascope-assets** Cloud Storage Buckets.
- Responsible for updating the corresponding acquisition documents on the Firestore DB as thier assets appear in the Bucket.
- Responsible for sending a pubsub trigger to the **pdf-builder** runtime when all the assets for the acqusition document have appeared.

### Deployment
All pushes to this directory automatically trigger a workflow to deploy the Cloud Function to a GCP Project.   
The GitHub Actions workflow is defined in the ``.github/workflows/deploy-asset-create.yml`` file.

The command used to deploy the function is as follows
```bash
gcloud functions deploy asset-create \
--region $REGION \
--entry-point main \
--service-account $SAEMAIL \
--runtime python39 \
--trigger-event google.storage.object.finalize
--trigger-resource terrascope-assets
```
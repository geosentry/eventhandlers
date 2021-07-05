# acquisition-repeat

### Runtime
Platform: **Google Cloud Platform**  
Environment: **Cloud Functions**
Runtime: **go113** (Go 1.13)  

### Trigger
Trigger Type: **PubSub**  
Trigger Topic: **repeats**  

### Service Account Permissions
- **Cloud Datastore User** (Firestore)
- **PubSub Publisher** (Cloud Pub/Sub)  

### Function Flow  
!todo  
When an pubsub message is recieved, Query the **regions** collection for documents that have the 'next_acquisition' timestamp less than current UTC time. For each region document, publish either an acqbuild or visbuild trigger to the taskbuilds topic

### Deployment
All pushes to this directory automatically trigger a workflow to deploy the Cloud Function to a GCP Project.   
The GitHub Actions workflow is defined in the ``.github/workflows/deploy-acquisition-repeat.yml`` file.

The command used to deploy the function is as follows
```bash
gcloud functions deploy acquisition-repeat \
--region $REGION \
--service-account $SAEMAIL \
--runtime go113 \
--entry-point Main \
--trigger-topic repeats 
```
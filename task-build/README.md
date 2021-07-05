# task-build

### Runtime
Platform: **Google Cloud Platform**  
Environment: **Cloud Functions**
Runtime: **go113** (Go 1.13)  

### Trigger
Trigger Type: **PubSub**  
Trigger Topic: **taskbuilds**  

### Service Account Permissions
- **Cloud Task ??** (Cloud Tasks)

### Function Flow  
!todo  
When an pubsub message is recieved, Create a Cloud Task based on the type on message trigger attribute.
- For 'acqbuild' triggers, create a task to send a HTTP request to the 'acqbuilder' core service.
- For 'visbuild' triggers, create a task to send a HTTP request to the 'visbuilder' core service.
- For 'topobuild' triggers, create a task to send a HTTP request to the 'topobuilder' core service.
- For 'nltxbuild' triggers, create a task to send a HTTP request to the 'analyticsbuilder' core service.

### Deployment
All pushes to this directory automatically trigger a workflow to deploy the Cloud Function to a GCP Project.   
The GitHub Actions workflow is defined in the ``.github/workflows/deploy-task-build.yml`` file.

The command used to deploy the function is as follows
```bash
gcloud functions deploy task-build \
--region $REGION \
--service-account $SAEMAIL \
--runtime go113 \
--entry-point Main \
--trigger-topic taskbuilds 
```
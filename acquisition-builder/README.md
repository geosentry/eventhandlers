# acquisiton-builder

### Runtime
Platform: **Google Cloud Platform**  
Environment: **Cloud Functions**
Runtime: **python39** (Python 3.9)  

### Trigger
Trigger Type: **PubSub**  
Trigger Topic: **acquisition-builds**  

### Service Account Permissions
Default Credentials
- **Secret Manager Secret Accessor** (Secret Manager)  
- **Cloud Datastore User** (Firestore)

Earth Engine Credentials (Stored on Secret Manager)
- **Earth Engine** (Registered as an Earth Engine SA)
- **Storage Object Admin** (Cloud Storage)

### Function Flow
1. Obtain the path to the *region* document by parsing the event dictionary from the PubSub trigger.
2. Initialize the Firestore Client and Earth Engine Session.
3. Validate that the *region* document is active for acquisitions. (not sure if this check is necessary. needs to be revisited)
4. Construct the geometry from geojson in the *region* document.
5. Check if the 'next_acquisition' field is set in the *region* document.
    - If the field is set, generate a datetime object from it.
    - Otherwise, find the latest acquisition available for the region and generate a datetime object from it.
6. Generate the acquisition image for the latest expected acquisition date and retrieve its Earth Engine Asset ID.
7. Update the *region* document's 'next_acquisition' and 'last_acquisition' fields.
8. Check the cloudiness of the acquisition. (TODO)
9. Generate the asset images based on the *region* document's subscription type.
10. Export the asset images to Cloud Storage Buckets through the Earth Engine Batch System.
11. Create the *acquisition* document with the acquisition metadata, asset export paths, etc.

### Deployment
All pushes to this directory automatically trigger a workflow to deploy the Cloud Function to a GCP Project.   
The GitHub Actions workflow is defined in the ``.github/workflows/deploy-acquisition-builder.yml`` file.

The command used to deploy the function is as follows
```bash
gcloud functions deploy acquisition-builder \
--region $REGION \
--entry-point main \
--service-account $SAEMAIL \
--runtime python39 \
--trigger-topic acquisition-builds 
```
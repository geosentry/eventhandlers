# asset-create

### Runtime
Platform: **Google Cloud Platform**  
Environment: **Cloud Functions**
Runtime: **python39** (Python 3.9)  

### Trigger
Trigger Type: **Cloud Storage**  
Trigger Event: **google.storage.object.finalize**
Trigger Resource: **geosentry-assets** 

### Service Account Permissions
- **Storage Object Admin** (Cloud Storage)  
- **Cloud Datastore User** (Firestore)

### Function Flow
1. Obtain the bucket name, file name and the content type from the event dictionary.
2. Check the content type and start the appropriate runtime for either PNG or GeoTIFF assets. Function terminates for any other content type.

GeoTIFF Runtime

1. Initialize the Storage Client and Bucket Handler.
2. Download the GeoTIFF Image Blob from the Cloud Storage Bucket.
3. Convert the GeoTIFF into a PNG.
4. Upload the PNG to the Cloud Storage Bucket.
5. Delete the GeoTIFF blob from the Cloud Storage Bucket.

PNG Runtime

1. Initialize Firestore Client.
2. Generate the path to the corresponding document from the asset filename.
3. Update the asset document with the path to the file in the Bucket.

### Deployment
All pushes to this directory automatically trigger a workflow to deploy the Cloud Function to a GCP Project.   
The GitHub Actions workflow is defined in the ``.github/workflows/deploy-asset-create.yml`` file.

The command used to deploy the function is as follows
```bash
gcloud functions deploy asset-create \
--region $REGION \
--service-account $SAEMAIL \
--runtime python39 \
--memory 1024MB \
--entry-point main \
--trigger-event google.storage.object.finalize \
--trigger-resource geosentry-assets
```
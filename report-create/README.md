# report-create
- This cloud function is responsible for handling object creation events for the **terrascope-reports** Cloud Storage Bucket.
- Responsible for sending a pubsub trigger to the **email-builder** for the 'subscription-report' runtime.
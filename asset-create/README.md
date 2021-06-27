# asset-create
- This cloud function is responsible for handling object creation events for the **terrascope-assets** Cloud Storage Buckets.
- Responsible for updating the corresponding acquisition documents on the Firestore DB as thier assets appear in the Bucket.
- Responsible for sending a pubsub trigger to the **pdf-builder** runtime when all the assets for the acqusition document have appeared.
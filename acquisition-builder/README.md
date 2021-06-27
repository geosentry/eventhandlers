# acquisiton-builder
- This cloud function/run container is responsible for handling pubsub messages from the **acquistion-builds** Pubsub Topic.
- Responsible for interacting with the Earth Engine API to generate spectral analytics for acquistions based on the region subscription.
- Responsible for exporting the spectral analytics data to the **terrascope-assets** Cloud Storage Bucket through the Earth Engine Batch Export System
- Responsible for creating the **acquisiton** documents in the Firestore DB for the corresponding region with the asset data, timestamps, etc.
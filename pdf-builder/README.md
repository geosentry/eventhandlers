# pdf-builder
- This cloud function is responsible for handling pubsub messages from the **pdf-builds** Pubsub Topic.
- Responsible for creating the the PDF reports for either analytical or visual assets depending on the message trigger.
- Responsible for reading report assets from either the **terrascope-assets** or **terrascope-visuals** Cloud Storage Buckets depending on the message trigger.
- Responsible for writing the PDF reports to the **terrascope-reports** Cloud Storage Bucket
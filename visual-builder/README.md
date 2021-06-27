# visual-builder
- This cloud function/run container is responsible for handling pubsub messages from the **visual-builds** Pubsub Topic.
- Responsible for interacting with the Earth Engine API to generate visual imagery from selected locations across the world.
- Responsible for exporting the image data to the **terrascope-visuals** Cloud Storage Bucket through the Earth Engine Batch Export System.
- Responsible for sending a pubsub trigger to the **pdf-builder** runtime when all the assets for the visuals catalog have appeared.

# region-create
- Status: Complete
- This cloud function is responsible for handling creation events for documents in the **'regions'** collection of the Firestore Database
- Responsible for sending a pubsub trigger to the **email-builder** for the 'new-region' runtime.
- Responsible for sending a pubsub trigger to the **acquisition-builder** runtime.
# region-update
- This cloud function is responsible for handling update events for documents in the **'regions'** collection of the Firestore Database
- Responsible for sending a pubsub trigger to the **email-builder** for the 'update-region-subscription' or the 'update-region-deactivate' runtime.
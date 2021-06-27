# user-create
- This cloud function is responsible for handling user creation events from Firebase Authentication
- Responsible for sending a pubsub trigger to the **email-builder** for the 'new-user' runtime.
# acquisition-checker
- This cloud function is responsible for handling pubsub messages from the **acquisition-checks** Pubsub Topic.
- Responsible for finding all regions that are due for a acquisiton and sending a pubsub trigger to the **acquisition-builder** runtime
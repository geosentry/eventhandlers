# region-create
Cloud Function Event Handler

## Status
**Hosted: True**  
**Development: Complete**  

## Functionality
- Trigger: On create of a document in the **regions** collection of Firestore
- Actions:
    - Collects the path of the document that was creates
    - Publishes the message (document path) to the **email-builds** PubSub topic with the 'runtime' attribute set to *new-region*
    - Publishes the message (document path) to the **acquisition-builds** PubSub topic

/*
GeoSentry Event Handler

Google Cloud Platform - Cloud Functions

region-create service
*/
package function

import (
	"context"
	"fmt"
	"strings"
	"time"

	"cloud.google.com/go/pubsub"
)

// A structure that represents a generic Region Document
// Only implements fields relevant to this service.
type RegionDoc struct {
	Type struct {
		StringValue string `json:"stringValue"`
	} `json:"type"`

	GeoJSON struct {
		StringValue string `json:"stringValue"`
	} `json:"geojson"`
}

// A structure that reprsents a Document Snapshot
// Specification: https://firebase.google.com/docs/firestore/reference/rest/v1beta1/projects.databases.documents
type FirestoreDocument struct {
	Name       string    `json:"name"`
	Fields     RegionDoc `json:"fields"`
	CreateTime time.Time `json:"createTime"`
	UpdateTime time.Time `json:"updateTime"`
}

// A structure that represents a Cloud Firestore Event
// Specification: https://cloud.google.com/functions/docs/calling/cloud-firestore#event_structure
type FirestoreEvent struct {
	Value      FirestoreDocument `json:"value"`
	OldValue   FirestoreDocument `json:"oldValue"`
	UpdateMask struct {
		FieldPaths []string `json:"fieldPaths"`
	} `json:"updateMask"`
}

func (event *FirestoreEvent) getDocPath() string {
	splitpath := strings.Split(event.Value.Name, "documents/")
	return splitpath[len(splitpath)-1]
}

func (event *FirestoreEvent) getProjectID() string {
	splitpath := strings.Split(event.Value.Name, "/")
	return splitpath[1]
}

// Cloud Functions Entrypoint
func Main(ctx context.Context, event FirestoreEvent) error {
	// Construct a new log entry
	log := NewLogEntry()

	// Retrieve the document path from the event data
	docpath := event.getDocPath()
	// Retrieve the project ID from the event data
	project := event.getProjectID()
	log.addtrace(fmt.Sprintf("event data read. docpath - %s.", docpath))

	// TODO: read geojson field
	// TODO: make http request to the geocore API's reshape endpoint
	// TODO: update the region document geojson

	// Create a PubSub Client
	client, err := pubsub.NewClient(ctx, project)
	if err != nil {
		// Log and exit
		log.addtrace("execution broke - could not initialize pubsub client.")
		log.flush("ALERT", "system error")
		return nil
	}
	// Defer the closing of the PubSub Client
	defer client.Close()
	log.addtrace("pubsub client initialized.")

	// Create a PubSub Topic Handler
	topic := client.Topic("taskbuilds")
	log.addtrace("pubsub topic created.")

	// Declare a buildflow string
	var buildflow string

	// Check the type of the region document
	switch event.Value.Fields.Type.StringValue {
	// Visual Region
	case "vis-region":
		// Set the buildflow
		buildflow = "new-vis-region"
		log.addtrace("vis-region detected.")

	// User Region
	case "user-region":
		// Set the buildflow
		buildflow = "new-acq-region"
		log.addtrace("user-region detected.")

	// Unsupported Region
	default:
		// Log the unsupported type and exit
		log.addtrace(fmt.Sprintf("unsupported region type detected. type - %s", event.Value.Fields.Type.StringValue))
		log.flush("WARNING", "runtime error")
		return nil
	}

	// Publish the document path and buildflow
	// attribute to the 'taskbuilds' topic
	result := topic.Publish(ctx, &pubsub.Message{
		Data: []byte(docpath),
		Attributes: map[string]string{
			"runtime": buildflow,
		},
	})

	// Check the publish result
	id, err := result.Get(ctx)
	if err != nil {
		// Log and exit
		log.addtrace(fmt.Sprintf("execution broke - could not publish pubsub message. error - %s", err))
		log.flush("CRITICAL", "runtime error")
		return nil
	}
	// Log the publish ID and exit
	log.addtrace(fmt.Sprintf("pubsub message published. topic - taskbuilds. runtime - %s. publishID - %s", buildflow, id))
	log.flush("INFO", "runtime complete")
	return nil
}

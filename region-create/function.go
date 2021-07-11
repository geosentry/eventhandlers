/*
GeoSentry Event Handler

Google Cloud Platform - Cloud Functions

region-create service
*/
package function

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"

	metadata "cloud.google.com/go/compute/metadata"
	firestore "cloud.google.com/go/firestore"
	pubsub "cloud.google.com/go/pubsub"
	servicedirectory "cloud.google.com/go/servicedirectory/apiv1"

	sdpb "google.golang.org/genproto/googleapis/cloud/servicedirectory/v1"
)

type ReshapeResponse struct {
	Bounds []float32          `json:"bounds"`
	Areas  map[string]float32 `json:"areas"`
}

// Cloud Functions Entrypoint
func Main(ctx context.Context, event FirestoreEvent) error {
	// Construct a new log entry
	log := NewLogEntry()

	// Retrieve the document path from the event data
	docpath := event.getDocPath()
	log.addtrace(fmt.Sprintf("event data read. docpath - %s.", docpath))

	// Retrieve the project ID from the env variables
	project := os.Getenv("GCP_PROJECT")
	// Retrieve the project region from the env variables
	projectregion := os.Getenv("GCP_REGION")

	// Create a Firestore Client
	dbclient, err := firestore.NewClient(ctx, project)
	if err != nil {
		// Log and exit
		log.addtrace("execution broke - could not initialize firestore client.")
		log.flush("ALERT", "system error")
		return nil
	}
	// Defer the closing of the Firestore Client
	defer dbclient.Close()
	log.addtrace("firestore client initialized.")

	// Construct a document reference to the Region
	regiondoc := dbclient.Doc(docpath)
	// Create a slice of Firestore updates and initialize
	// it with the Delete sentinel for the geojson field
	updates := []firestore.Update{{Path: "geojson", Value: firestore.Delete}}

	// Create a Service Directory Lookup Client
	resolver, err := servicedirectory.NewLookupClient(ctx)
	if err != nil {
		// Log and exit
		log.addtrace("execution broke - could not initialize service lookup client.")
		log.flush("ALERT", "system error")
		return nil
	}
	// Defer the closing of the Firestore Client
	defer resolver.Close()
	log.addtrace("service lookup client initialized.")

	// Construct the service name for the 'geocore-spatio' service
	servicename := fmt.Sprintf("projects/%s/locations/%s/namespaces/geocore/services/geocore-spatio", project, projectregion)
	// Create a resolve request for the 'geocore-spatio' service
	resolverequest := &sdpb.ResolveServiceRequest{Name: servicename}
	// Resolve the service and obtain its information
	resolveresponse, err := resolver.ResolveService(ctx, resolverequest)
	if err != nil {
		// Log and exit
		log.addtrace("execution broke - could not resolve the geocore-spatio service.")
		log.flush("ALERT", "system error")
		return nil
	}
	log.addtrace("geocore-spatio service resolved.")

	// Retrieve the URL of the 'geocore-spatio' service from its annotations
	url := resolveresponse.Service.Annotations["url"]
	// Create the URL for the reshape endpoint of the 'geocore-spatio' service.
	reshapeURL := fmt.Sprintf("%s/reshape", url)
	// Create the URL for the geocode endpoint of the 'geocore-spatio' service.
	//geocodeURL := fmt.Sprintf("%s/geocode", url)

	log.addtrace("service URLs generated.")

	// Retrieve the data of the 'geojson' field from the event data
	geojson := event.Value.Fields.GeoJSON.StringValue
	// Construct the request body with the geojson data to reshape
	var requestbody = []byte(fmt.Sprintf(`{"geojson": %s}`, geojson))
	// Construct the request object
	request, err := http.NewRequest("POST", reshapeURL, bytes.NewBuffer(requestbody))
	if err != nil {
		log.addtrace("")
	}
	log.addtrace("reshape request body generated.")

	// Set the Content-Type and User-Agent headers of the request
	request.Header.Set("User-Agent", "region-create cloud function")
	request.Header.Set("Content-Type", "application/json")

	// Retrieve authentication token from the GCP Compute Metadata API for the reshape service URL
	reshapetokenURL := fmt.Sprintf("/instance/service-accounts/default/identity?audience=%s", reshapeURL)
	reshapetoken, err := metadata.Get(reshapetokenURL)
	if err != nil {
		log.addtrace("")
	}
	// Set the Authorization Header of the request
	request.Header.Set("Authorization", fmt.Sprintf("Bearer %s", reshapetoken))

	log.addtrace("reshape request headers generated.")

	// Create a HTTP Client
	netclient := &http.Client{}
	// Perform the HTTP request
	response, err := netclient.Do(request)
	if err != nil {
		log.addtrace("")
	}
	defer response.Body.Close()

	body, err := ioutil.ReadAll(response.Body)
	if err != nil {
		log.addtrace("")
	}

	var reshaperesponse ReshapeResponse
	json.Unmarshal(body, &reshaperesponse)

	// add bounds and area data to region document
	updates = append(updates, firestore.Update{Path: "bounds", Value: reshaperesponse.Bounds})
	updates = append(updates, firestore.Update{Path: "namenew", Value: reshaperesponse.Areas})

	// TODO: geocoding
	// construct request object with bounds data
	// retrieve idtoken from computemeta api for geocode and set auth header
	// make HTTP request to geocode and collect response data
	// add geocode data to the region document

	// Update the region document to firestore.
	regiondoc.Update(ctx, updates)

	// Create a PubSub Client
	pusbsubclient, err := pubsub.NewClient(ctx, project)
	if err != nil {
		// Log and exit
		log.addtrace("execution broke - could not initialize pubsub client.")
		log.flush("ALERT", "system error")
		return nil
	}
	// Defer the closing of the PubSub Client
	defer pusbsubclient.Close()
	log.addtrace("pubsub client initialized.")

	// Create a PubSub Topic Handler
	topic := pusbsubclient.Topic("taskbuilds")
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

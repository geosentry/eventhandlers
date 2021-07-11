package regioncreate

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"sync"

	metadata "cloud.google.com/go/compute/metadata"
	firestore "cloud.google.com/go/firestore"
	pubsub "cloud.google.com/go/pubsub"
	servicedirectory "cloud.google.com/go/servicedirectory/apiv1"
	sdpb "google.golang.org/genproto/googleapis/cloud/servicedirectory/v1"
)

type RegionCreate struct {
	// Represents
	log *LogEntry
	ctx context.Context
	wg  *sync.WaitGroup

	ProjectID     string
	ProjectRegion string
	Event         FirestoreEvent

	HTTPClient      *http.Client
	GeoCoreURLs     map[string]string
	ReshapeResponse struct {
		Bounds []float32          `json:"bounds"`
		Areas  map[string]float32 `json:"areas"`
	}

	DBClient         *firestore.Client
	RegionDoc        *firestore.DocumentRef
	RegionDocUpdates []firestore.Update

	PubSubClient *pubsub.Client
	BuildTopic   *pubsub.Topic
	BuildMessage *pubsub.Message

	Broken  bool
	ErrChan chan error
	LogChan chan string
}

func (runner *RegionCreate) Close() {
	runner.DBClient.Close()
	runner.PubSubClient.Close()
}

func (runner *RegionCreate) StartLogger() {
	// Construct a new log entry and set it to the runner
	runner.log = NewLogEntry("region-create")

	// Infinite Loop
	for {
		// Listen on the context, log and error channels
		select {
		// Add log to traces
		case log := <-runner.LogChan:
			runner.log.addtrace(log)

		// Add error log to traces
		case err := <-runner.ErrChan:
			runner.log.addtrace(fmt.Sprintf("error: %s.", err))
			runner.Broken = true

		// Add execution break and return
		case <-runner.ctx.Done():
			runner.log.addtrace("execution broke.")
			return
		}
	}
}

func (runner *RegionCreate) Setup(ctx context.Context, event FirestoreEvent) context.CancelFunc {
	// Create a cancellable context and set it to the runner
	cntx, cancel := context.WithCancel(ctx)
	runner.ctx = cntx

	// Set the event data
	runner.Event = event
	// Create and set the HTTP Client
	runner.HTTPClient = &http.Client{}
	// Retrieve and set the project ID from the env variables
	runner.ProjectID = os.Getenv("GCP_PROJECT")
	// Retrieve and set the project region from the env variables
	runner.ProjectRegion = os.Getenv("GCP_REGION")

	// Return the context cancel function
	return cancel
}

func (runner *RegionCreate) SetupDB() {
	// Defer the completion for the waitgroup
	defer runner.wg.Done()

	// Create a Firestore Client
	client, err := firestore.NewClient(runner.ctx, runner.ProjectID)
	if err != nil {
		runner.ErrChan <- fmt.Errorf("could not initialize firestore client")
		return
	}

	// Set the firestore client to the runner
	runner.DBClient = client
	// Construct a document reference for the Region
	runner.RegionDoc = runner.DBClient.Doc(runner.Event.getDocPath())
	// Create an empty slice of Firestore Updates
	runner.RegionDocUpdates = make([]firestore.Update, 0)
}

func (runner *RegionCreate) SetupPubSub() {
	// Defer the completion for the waitgroup
	defer runner.wg.Done()

	// Create a PubSub Client
	client, err := pubsub.NewClient(runner.ctx, runner.ProjectID)
	if err != nil {
		runner.ErrChan <- fmt.Errorf("could not initialize pubsub client")
	}

	// Set the PubSub client to the runner
	runner.PubSubClient = client
	// Create a PubSub Topic Handler
	runner.BuildTopic = client.Topic("taskbuilds")
	// Create a PubSub Message
	runner.BuildMessage = &pubsub.Message{Data: []byte(runner.Event.getDocPath())}

	// Check the type of the region document and set the runtime attribute
	switch runner.Event.Value.Fields.Type.StringValue {
	// Visual Region
	case "vis-region":
		// Set the runtime attribute
		runner.BuildMessage.Attributes = map[string]string{"runtime": "new-vis-region"}
		runner.LogChan <- "vis region detected."

	// User Acq Region
	case "acq-region":
		// Set the runtime attribute
		runner.BuildMessage.Attributes = map[string]string{"runtime": "new-acq-region"}
		runner.LogChan <- "acq region detected."

	// Unsupported Region
	default:
		runner.ErrChan <- fmt.Errorf("unsupported region type: %s", runner.Event.Value.Fields.Type.StringValue)
		return
	}
}

func (runner *RegionCreate) ResolveGeoCoreService() {
	// Defer the completion for the waitgroup
	defer runner.wg.Done()

	// Create a Service Directory Lookup Client
	client, err := servicedirectory.NewLookupClient(runner.ctx)
	if err != nil {
		runner.ErrChan <- fmt.Errorf("could not initialize service lookup client")
		return
	}
	// Defer the closing of the Lookup Client
	defer client.Close()

	// Construct the service name for the 'geocore-spatio' service
	servicename := fmt.Sprintf("projects/%s/locations/%s/namespaces/geocore/services/geocore-spatio", runner.ProjectID, runner.ProjectRegion)

	// Create a resolve request for the 'geocore-spatio' service
	resolverequest := &sdpb.ResolveServiceRequest{Name: servicename}
	// Resolve the service and obtain its information
	resolveresponse, err := client.ResolveService(runner.ctx, resolverequest)
	if err != nil {
		runner.ErrChan <- fmt.Errorf("could not resolve the geocore-spatio service")
		return
	}

	// Retrieve the URL of the 'geocore-spatio' service from its annotations
	url := resolveresponse.Service.Annotations["url"]
	// Create the URLs for the reshape and geocode endpoints.
	runner.GeoCoreURLs = map[string]string{
		"reshape": fmt.Sprintf("%s/reshape", url),
		"geocode": fmt.Sprintf("%s/geocode", url),
	}
}

func (runner *RegionCreate) Reshape() {
	// Retrieve the data of the 'geojson' field from the event data
	geojson := runner.Event.Value.Fields.GeoJSON.StringValue
	url := runner.GeoCoreURLs["reshape"]

	// Construct the request body with the geojson data to reshape
	var requestbody = []byte(fmt.Sprintf(`{"geojson": %s}`, geojson))
	// Construct the request object
	request, err := http.NewRequest("POST", url, bytes.NewBuffer(requestbody))
	if err != nil {
		runner.ErrChan <- fmt.Errorf("could not build reshape request body")
		return
	}

	// Set the Content-Type and User-Agent headers of the request
	request.Header.Set("User-Agent", "region-create cloud function")
	request.Header.Set("Content-Type", "application/json")

	// Retrieve authentication token from the GCP Compute Metadata API
	tokenurl := fmt.Sprintf("/instance/service-accounts/default/identity?audience=%s", url)
	token, err := metadata.Get(tokenurl)
	if err != nil {
		runner.ErrChan <- fmt.Errorf("could not build reshape request body")
		return
	}

	// Set the Authorization Header of the request
	request.Header.Set("Authorization", fmt.Sprintf("Bearer %s", token))

	// Perform the HTTP request
	response, err := runner.HTTPClient.Do(request)
	if err != nil {
		runner.ErrChan <- fmt.Errorf("could not post reshape request")
		return
	}
	defer response.Body.Close()
	// Read the response data
	responsebody, err := ioutil.ReadAll(response.Body)
	if err != nil {
		runner.ErrChan <- fmt.Errorf("could not read reshape response")
		return
	}

	// Unmarshall response into a ReshapeResponse
	json.Unmarshal(responsebody, &runner.ReshapeResponse)
}

func (runner *RegionCreate) Geocode() {}

func (runner *RegionCreate) Update() {
	// Defer the completion for the waitgroup
	defer runner.wg.Done()

	// Get Reshaped Bounds of the Region
	runner.Reshape()
	runner.LogChan <- "region reshape complete."

	// Get Geocoding Data of the Region
	// runner.Geocode()
	// runner.LogChan <- "region geocode complete."

	// TODO: geocoding
	// construct request object with centroid data
	// retrieve idtoken from computemeta api for geocode and set auth header
	// make HTTP request to geocode and collect response data
	// add geocode data to the region document

	// Accumulate updates for the region document
	runner.RegionDocUpdates = append(
		runner.RegionDocUpdates,
		firestore.Update{Path: "geojson", Value: firestore.Delete},
		firestore.Update{Path: "bounds", Value: runner.ReshapeResponse.Bounds},
		firestore.Update{Path: "areas", Value: runner.ReshapeResponse.Bounds},
		// firestore.Update{Path: "centroid", Value: runner.ReshapeResponse.Centroid},
		// firestore.Update{Path: "geocode", Value: runner.GeocodeResponse},
	)

	// Update the region document to Firestore.
	runner.RegionDoc.Update(runner.ctx, runner.RegionDocUpdates)
	runner.LogChan <- "region update complete."
}

func (runner *RegionCreate) Publish() {
	// Publish the build message to the topic
	result := runner.BuildTopic.Publish(runner.ctx, runner.BuildMessage)

	// Check the publish result
	id, err := result.Get(runner.ctx)
	if err != nil {
		runner.ErrChan <- fmt.Errorf("could not publish build message. %s", err)
		return
	}
	runner.LogChan <- fmt.Sprintf("pubsub message published. publish ID - %s", id)
}

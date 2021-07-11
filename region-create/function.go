/*
GeoSentry Event Handler

Google Cloud Platform - Cloud Functions

region-create service
*/
package regioncreate

import (
	"context"
)

// Cloud Functions Entrypoint
func Main(ctx context.Context, event FirestoreEvent) error {
	// Create a new region-create runner
	runner := RegionCreate{}
	// Defer the closing of cloud clients
	defer runner.Close()

	// Start the runner logger
	runner.StartLogger()

	// Setup the runner execution
	cancel := runner.Setup(ctx, event)
	runner.LogChan <- "execution setup complete."

	runner.wg.Add(2)
	// Setup the Firestore DB
	go runner.SetupDB()
	// Resolve the GeoCore services
	go runner.ResolveGeoCoreService()
	// Wait for execution group to complete
	runner.wg.Wait()
	// Check if the execution broke
	if runner.Broken {
		// Close the logger, flush it and exit
		cancel()
		runner.log.flush("ALERT", "runtime error")
		return nil
	}
	runner.LogChan <- "db setup and service resolve complete."

	runner.wg.Add(2)
	// Setup PubSub
	go runner.SetupPubSub()
	// Update the Region document
	go runner.Update()
	// Wait for execution group to complete
	runner.wg.Wait()
	// Check if the execution broke
	if runner.Broken {
		// Close the logger, flush it and exit
		cancel()
		runner.log.flush("ALERT", "runtime error")
		return nil
	}
	runner.LogChan <- "pubsub setup complete."

	// Publish the build message for the region
	runner.Publish()
	// Check if the execution broke
	if runner.Broken {
		// Close the logger, flush it and exit
		cancel()
		runner.log.flush("ALERT", "runtime error")
		return nil
	}

	// Close the logger, flush it and exit
	cancel()
	runner.log.flush("INFO", "runtime complete")
	return nil
}

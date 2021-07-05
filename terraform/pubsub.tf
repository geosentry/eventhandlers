# Enable Cloud Pub/Sub API
resource "google_project_service" "pubsub-api" {
  service = "pubsub.googleapis.com"
  disable_on_destroy = false
}

# Create for PubSub Topic for taskbuilds
resource "google_pubsub_topic" "taskbuilds" {
  name = "taskbuilds"
}

# Create for PubSub Topic for cleanups
resource "google_pubsub_topic" "cleanups" {
  name = "cleanups"
}

# Create for PubSub Topic for repeats
resource "google_pubsub_topic" "repeats" {
  name = "repeats"
}
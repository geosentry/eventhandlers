# Enable Firestore API
resource "google_project_service" "firestore-api" {
  service = "firestore.googleapis.com"
  disable_on_destroy = false
}

# TODO: Create Firestore Index and Collection Groups
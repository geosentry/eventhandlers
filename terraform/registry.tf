# Enable Arifact Registry API
resource "google_project_service" "artifactregistry-api" {
  service = "artifactregistry.googleapis.com"
  disable_on_destroy = false
}

# TODO: Create the Python Format Repository
# TODO: Create the Docker Format Repository
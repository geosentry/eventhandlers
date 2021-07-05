# Enable Google Earth Engine API
resource "google_project_service" "earthengine-api" {
  service = "earthengine.googleapis.com"
  disable_on_destroy = false
}

# Enable Cloud Functions API
resource "google_project_service" "cloudfunctions-api" {
  service = "cloudfunctions.googleapis.com"
  disable_on_destroy = false
}

# Enable Cloud Run API
resource "google_project_service" "cloudrun-api" {
  service = "run.googleapis.com"
  disable_on_destroy = false
}

# Enable Cloud Build API
resource "google_project_service" "cloudbuild-api" {
  service = "cloudbuild.googleapis.com"
  disable_on_destroy = false
}


# Enable Secret Manager API
resource "google_project_service" "secretmanager-api" {
  service = "secretmanager.googleapis.com"
  disable_on_destroy = false
}

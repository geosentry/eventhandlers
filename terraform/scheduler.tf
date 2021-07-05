# Enable Cloud Scheduler API
resource "google_project_service" "cloudscheduler-api" {
  service = "cloudscheduler.googleapis.com"
  disable_on_destroy = false
}

# TODO: Create Scheduler Jobs for cleanups and repeats
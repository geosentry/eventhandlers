# Enable Cloud Tasks API
resource "google_project_service" "cloudtasks-api" {
  service = "cloudtasks.googleapis.com"
  disable_on_destroy = false
}

# TODO: Create Task Queues for core services
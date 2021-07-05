# Enable Cloud Storage API
resource "google_project_service" "storage-api" {
  service = "storage.googleapis.com"
  disable_on_destroy = false
}

# Create a Cloud Storage Bucket
resource "google_storage_bucket" "asset-bucket" {
  name          = "geosentry-assets"
  location      = "ASIA-SOUTH1"

  force_destroy = true
  uniform_bucket_level_access = true

  # Define Lifecycle rule to destroy 
  # objects older than 60 days
  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 60
    }
  }
}

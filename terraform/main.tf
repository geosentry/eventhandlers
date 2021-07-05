terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 3.53"
    }
  }
}

variable "project" {
  type        = string
  description = "Google Cloud Platform Project ID"
}

variable "region" {
  type    = string
  default = "asia-south1"
  description = "Google Cloud Platform Deployment Region"
}

provider "google" {
  region = "asia-south1"
  project = var.project
}

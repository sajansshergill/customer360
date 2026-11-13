terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_bigquery_dataset" "bronze" {
  dataset_id = "${var.dataset_prefix}_bronze"
  location   = var.region
}

resource "google_bigquery_dataset" "silver" {
  dataset_id = "${var.dataset_prefix}_silver"
  location   = var.region
}

resource "google_bigquery_dataset" "gold" {
  dataset_id = "${var.dataset_prefix}_gold"
  location   = var.region
}

resource "google_storage_bucket" "landing" {
  name     = "${var.project_id}-${var.dataset_prefix}-landing"
  location = var.region
  uniform_bucket_level_access = true
}

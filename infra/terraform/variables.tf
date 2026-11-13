variable "project_id" {
  type        = string
  description = "GCP project id"
}

variable "region" {
  type        = string
  default     = "us-central1"
  description = "Default region for BQ datasets and GCS"
}

variable "dataset_prefix" {
  type        = string
  default     = "consumer360"
  description = "Prefix for bronze/silver/gold datasets"
}

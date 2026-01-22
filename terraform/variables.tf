variable "project_id" {
  description = "The GCP project ID"
  type        = string
  default     = "job-spotter-485100"
}

variable "region" {
  description = "The GCP region"
  type        = string
  default     = "europe-west1"
}

variable "env" {
  description = "The development environment (e.g., dev, prod)"
  type        = string
  default     = "prod"
}

variable "db_password" {
  description = "The password for the Cloud SQL user"
  type        = string
  sensitive   = true
}

variable "github_repository" {
  description = "The GitHub repository in the format OWNER/REPO"
  type        = string
}

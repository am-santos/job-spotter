resource "google_service_account" "gsa" {
  account_id = "${var.env}-gsa"

  display_name = "Cloud Run Service Account"
}

# Bind GSA to Vertex AI User role
resource "google_project_iam_member" "vertex_ai_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.gsa.email}"
}

# Cloud SQL Client role
resource "google_project_iam_member" "cloudsql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.gsa.email}"
}

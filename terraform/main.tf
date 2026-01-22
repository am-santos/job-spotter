resource "google_cloud_run_v2_service" "app" {
  name     = "${var.env}-app"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.repo.name}/job-spotter:latest"


      env {
        name  = "POSTGRES_DB"
        value = google_sql_database.default.name
      }
      env {
        name  = "POSTGRES_USER"
        value = google_sql_user.user.name
      }
      env {
        name  = "POSTGRES_PASSWORD"
        value = google_sql_user.user.password
      }
      env {
        name  = "DB_HOST"
        value = google_sql_database_instance.postgres.private_ip_address
      }
      env {
        name  = "DB_PORT"
        value = "5432"
      }

      env {
        name  = "CELERY_BROKER_URL"
        value = "redis://${google_redis_instance.cache.host}:${google_redis_instance.cache.port}/0"
      }

      resources {
        limits = {
          cpu    = "1000m"
          memory = "512Mi"
        }
      }
    }

    vpc_access {
      connector = google_vpc_access_connector.connector.id
      egress    = "ALL_TRAFFIC"
    }

    service_account = google_service_account.gsa.email
  }

  depends_on = [
    google_project_iam_member.cloudsql_client,
    google_project_iam_member.vertex_ai_user,
    google_sql_database_instance.postgres,
    google_redis_instance.cache
  ]
}

# Allow public access to the service (optional, based on requirements.
# If internal only, remove this binding and change ingress to INTERNAL_LOAD_BALANCER or similar)
resource "google_cloud_run_service_iam_binding" "default" {
  location = google_cloud_run_v2_service.app.location
  service  = google_cloud_run_v2_service.app.name
  role     = "roles/run.invoker"
  members  = ["allUsers"]
}


resource "google_cloud_scheduler_job" "scraping_job" {
  name             = "${var.env}-scraping-job"
  description      = "Trigger scraping every 6 hours"
  schedule         = "0 */6 * * *"
  time_zone        = "Etc/UTC"
  attempt_deadline = "320s"

  http_target {
    http_method = "POST"
    uri         = "${google_cloud_run_v2_service.app.uri}/api/trigger-scraping/"

    oidc_token {
      service_account_email = google_service_account.gsa.email
    }
  }
}

resource "google_artifact_registry_repository_iam_member" "repo_writer" {
  location   = google_artifact_registry_repository.repo.location
  repository = google_artifact_registry_repository.repo.name
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${google_service_account.gsa.email}"
}

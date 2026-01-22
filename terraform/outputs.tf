output "project_id" {
  value = var.project_id
}

output "region" {
  value = var.region
}

output "vpc_name" {
  value = google_compute_network.vpc.name
}

output "vpc_id" {
  value = google_compute_network.vpc.id
}

output "db_connection_name" {
  value = google_sql_database_instance.postgres.connection_name
}

output "db_private_ip" {
  value = google_sql_database_instance.postgres.private_ip_address
}

output "redis_host" {
  value = google_redis_instance.cache.host
}

output "redis_port" {
  value = google_redis_instance.cache.port
}


output "cloud_run_url" {
  value = google_cloud_run_v2_service.app.uri
}

output "gsa_email" {
  value = google_service_account.gsa.email
}

output "artifact_registry_repo" {
  value = google_artifact_registry_repository.repo.name
}


resource "google_sql_database_instance" "postgres" {
  name             = "${var.env}-postgres-${random_id.db_name_suffix.hex}"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier              = "db-f1-micro"
    availability_type = "ZONAL"

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.vpc.id
    }
  }

  # Set to false for production
  deletion_protection = false

  depends_on = [google_service_networking_connection.private_vpc_connection]
}

resource "random_id" "db_name_suffix" {
  byte_length = 4
}

resource "google_sql_database" "default" {
  name     = "${var.env}-db"
  instance = google_sql_database_instance.postgres.name
}

resource "google_sql_user" "user" {
  name     = "${var.env}-user"
  instance = google_sql_database_instance.postgres.name
  password = var.db_password
}

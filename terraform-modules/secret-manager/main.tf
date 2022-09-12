resource "google_secret_manager_secret" "secret" {
  secret_id = "${var.app_name}-${var.secret_name}-${local.env}"

  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
}

resource "google_secret_manager_secret_version" "secret" {
  secret      = google_secret_manager_secret.secret.id
  secret_data = var.secret_value
}
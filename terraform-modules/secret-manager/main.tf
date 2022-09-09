resource "google_secret_manager_secret" "secret" {
  secret_id = "${var.app_name}-${var.secret_name}-${local.env}"

  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "secret" {
  secret      = google_secret_manager_secret.secret.id
  secret_data = var.secret_value

}
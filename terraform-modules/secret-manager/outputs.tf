output "secret_resource_id" {
  value = google_secret_manager_secret.secret.id
}

output "secret_version_name" {
  value = google_secret_manager_secret_version.secret.name
}

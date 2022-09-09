output "app_engine_service_id" {
  value = google_project_service.app_engine.id
}

output "cloud_functions_service_id" {
  value = google_project_service.cloud_functions.id
}

output "cloud_scheduler_service_id" {
  value = google_project_service.cloud_scheduler.id
}

output "iam_service_id" {
  value = google_project_service.iam.id
}

output "cloud_build_service_id" {
  value = google_project_service.cloud_build.id
}

output "secret_manager_service_id" {
  value = google_project_service.secret_manager.id
}

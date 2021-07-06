output "service_account_email" {
  value = google_service_account.function_runtime.email
}

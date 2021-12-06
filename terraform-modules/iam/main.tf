resource "random_string" "value" {
  length    = 5
  special   = false
  min_lower = 5
}

resource "google_service_account" "function_runtime" {
  account_id   = "${var.name}-${local.env}-${random_string.value.result}"
  display_name = "${var.name} function runtime ${local.env} "

  provisioner "local-exec" {
    command = "sleep 120"
  }
}

# Project level permissions are set here
# Organization level permissions are set using the console - see README for details
resource "google_project_iam_member" "permissions" {
  member   = "serviceAccount:${google_service_account.function_runtime.email}"
  for_each = toset(["roles/pubsub.publisher", "roles/pubsub.subscriber"])
  role     = each.key
}

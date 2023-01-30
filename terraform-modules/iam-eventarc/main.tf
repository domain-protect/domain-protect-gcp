resource "random_string" "value" {
  length    = 4
  special   = false
  min_lower = 4
}

resource "google_service_account" "eventarc" {
  account_id   = "${var.name}-event-${local.env}-${random_string.value.result}"
  display_name = "${var.name} Eventarc Trigger ${local.env} "

  provisioner "local-exec" {
    command = "sleep 120"
  }
}

resource "google_project_iam_member" "permissions" {
  member   = "serviceAccount:${google_service_account.eventarc.email}"
  project  = var.project
  for_each = toset(["roles/cloudfunctions.serviceAgent", "roles/run.invoker", "roles/eventarc.eventReceiver"])
  role     = each.key
}

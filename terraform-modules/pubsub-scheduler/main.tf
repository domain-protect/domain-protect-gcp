# pubsub topic to trigger functions
resource "google_pubsub_topic" "scheduler" {
  name = "${var.name}-scheduler-${local.env}"

  #checkov:skip=CKV_GCP_83: not opting to use KMS-based encryption key
}

# create an app engine application for scheduler to work in the project if none already
resource "google_app_engine_application" "function_scheduler" {
  count       = var.create_app_engine == true ? 1 : 0
  project     = var.project
  location_id = var.app_service_region
}

# scheduler - requires App service to be created in the project
resource "google_cloud_scheduler_job" "functions" {
  name        = "${var.name}-${local.env}"
  region      = var.app_service_region
  description = "Schedule for ${var.name} functions"
  schedule    = local.env == "dev" ? var.schedule_dev : var.schedule
  time_zone   = var.time_zone

  pubsub_target {
    topic_name = "projects/${var.project}/topics/${google_pubsub_topic.scheduler.name}"
    data       = "dHJpZ2dlcg==" #Base64 encoding of "trigger"
  }
}

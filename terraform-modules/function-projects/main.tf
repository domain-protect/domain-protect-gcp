# Dummy resource to ensure archive is created at apply stage
resource "null_resource" "dummy_trigger" {
  triggers = {
    timestamp = timestamp()
  }
}

# zip source code
data "archive_file" "code" {
  type        = "zip"
  source_dir  = "${path.module}/code/projects"
  output_path = "${path.module}/build/projects.zip"
  depends_on = [
    # Make sure archive is created in apply stage
    null_resource.dummy_trigger
  ]
}

# upload compressed code to bucket
resource "google_storage_bucket_object" "function" {
  name   = "projects-${data.archive_file.code.output_md5}.zip"
  bucket = var.bucket_name
  source = "${path.module}/build/projects.zip"
}

resource "google_cloudfunctions2_function" "function" {
  name        = "${var.name}-projects-${local.env}"
  description = "${var.name} Lists all projects in Organization and writes to ${local.env} Pub/Sub topic"
  location    = var.region

  build_config {
    runtime     = var.runtime
    entry_point = "projects"

    source {
      storage_source {
        bucket = var.bucket_name
        object = google_storage_bucket_object.function.name
      }
    }
  }

  service_config {
    timeout_seconds = var.timeout
    environment_variables = {
      SECURITY_PROJECT = var.project
      APP_ENVIRONMENT  = local.env
      APP_NAME         = var.name
    }
    all_traffic_on_latest_revision = true
    service_account_email          = var.service_account_email
    ingress_settings               = var.ingress_settings
  }

  event_trigger {
    trigger_region        = var.region
    event_type            = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic          = "projects/${var.project}/topics/${var.pubsub_topic}"
    service_account_email = var.service_account_eventarc
  }
}

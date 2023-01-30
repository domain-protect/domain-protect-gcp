# Dummy resource to ensure archive is created at apply stage
resource "null_resource" "dummy_trigger" {
  triggers = {
    timestamp = timestamp()
  }
}

# zip source code
data "archive_file" "code" {
  type        = "zip"
  source_dir  = "${path.module}/code/notify"
  output_path = "${path.module}/build/notify.zip"
  depends_on = [
    # Make sure archive is created in apply stage
    null_resource.dummy_trigger
  ]
}

# upload compressed code to bucket
resource "google_storage_bucket_object" "function" {
  name   = "notify-${data.archive_file.code.output_md5}.zip"
  bucket = var.bucket_name
  source = "${path.module}/build/notify.zip"
}

resource "google_cloudfunctions2_function" "function" {
  name        = "${var.name}-notify-${var.slack_channel}-${local.env}"
  description = "${var.name} Slack notification function to ${var.slack_channel} channel in ${local.env} environment"
  location    = var.region

  build_config {
    runtime     = var.runtime
    entry_point = "notify"

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
      SLACK_CHANNEL  = var.slack_channel
      SLACK_USERNAME = var.slack_username
      SLACK_EMOJI    = var.slack_emoji
    }
    all_traffic_on_latest_revision = true
    service_account_email          = var.service_account_email
    ingress_settings               = var.ingress_settings

    secret_environment_variables {
      key        = "SLACK_URL"
      project_id = var.project
      secret     = local.secret_id
      version    = local.secret_version
    }
  }

  event_trigger {
    trigger_region        = var.region
    event_type            = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic          = "projects/${var.project}/topics/${var.pubsub_topic}"
    service_account_email = var.service_account_eventarc
  }
}

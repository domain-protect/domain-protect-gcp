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

resource "google_cloudfunctions_function" "function" {
  name                  = "${var.name}-notify-${var.slack_channel}-${local.env}"
  description           = "${var.name} Slack notification function to ${var.slack_channel} channel in ${local.env} environment"
  source_archive_bucket = var.bucket_name
  source_archive_object = google_storage_bucket_object.function.name
  timeout               = var.timeout
  entry_point           = "notify"
  runtime               = var.runtime
  service_account_email = var.service_account_email
  ingress_settings      = var.ingress_settings

  environment_variables = {
    SLACK_CHANNEL  = var.slack_channel
    SLACK_USERNAME = var.slack_username
    SLACK_EMOJI    = var.slack_emoji
  }

  secret_environment_variables {
    key     = "SLACK_URL"
    secret  = local.secret_id
    version = local.secret_version
  }

  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = "projects/${var.project}/topics/${var.pubsub_topic}"
  }
}
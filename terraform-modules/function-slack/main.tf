# zip source code
data "archive_file" "code" {
  type        = "zip"
  source_dir  = "${path.module}/code/notify"
  output_path = "${path.module}/build/notify.zip"
}

# upload compressed code to bucket
resource "google_storage_bucket_object" "function" {
  name   = "notify-${data.archive_file.code.output_md5}.zip"
  bucket = var.bucket_name
  source = "${path.module}/build/notify.zip"
}

resource "google_cloudfunctions_function" "function" {
  count                 = length(var.slack_channels)
  name                  = "${var.name}-notify-${var.slack_channels[count.index]}-${local.env}"
  description           = "${var.name} Slack notification function to ${var.slack_channels[count.index]} channel in ${local.env} environment"
  source_archive_bucket = var.bucket_name
  source_archive_object = google_storage_bucket_object.function.name
  timeout               = var.timeout
  entry_point           = "notify"
  runtime               = var.runtime
  service_account_email = var.service_account_email
  ingress_settings      = var.ingress_settings

  environment_variables = {
    SLACK_CHANNEL     = element(var.slack_channels, count.index)
    SLACK_WEBHOOK_URL = element(var.slack_webhook_urls, count.index)
    SLACK_USERNAME    = var.slack_username
    SLACK_EMOJI       = var.slack_emoji
  }

  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = "projects/${var.project}/topics/${var.pubsub_topic}"
  }
}
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

resource "google_cloudfunctions_function" "function" {
  name                  = "${var.name}-projects-${local.env}"
  description           = "${var.name} Lists all projects in Organization and writes to ${local.env} Pub/Sub topic"
  source_archive_bucket = var.bucket_name
  source_archive_object = google_storage_bucket_object.function.name
  timeout               = var.timeout
  entry_point           = "projects"
  runtime               = var.runtime
  service_account_email = var.service_account_email
  ingress_settings      = var.ingress_settings

  environment_variables = {
    SECURITY_PROJECT = var.project
    APP_ENVIRONMENT  = local.env
    APP_NAME         = var.name
  }

  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = "projects/${var.project}/topics/${var.pubsub_topic}"
  }
}
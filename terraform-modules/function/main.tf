# zip source code
data "archive_file" "code" {
  count       = length(var.functions)
  type        = "zip"
  source_dir  = "${path.module}/code/${var.functions[count.index]}"
  output_path = "${path.module}/build/${var.functions[count.index]}.zip"
}

# upload compressed code to bucket
resource "google_storage_bucket_object" "function" {
  count  = length(var.functions)
  name   = "${var.functions[count.index]}-${data.archive_file.code.*.output_md5[count.index]}.zip"
  bucket = var.bucket_name
  source = "${path.module}/build/${var.functions[count.index]}.zip"
}

resource "google_cloudfunctions_function" "function" {
  count                         = length(var.functions)
  name                          = "${var.name}-${var.functions[count.index]}-${local.env}"
  description                   = "${var.name} ${var.functions[count.index]} function in ${local.env} environment"
  available_memory_mb           = var.available_memory
  source_archive_bucket         = var.bucket_name
  source_archive_object         = google_storage_bucket_object.function.*.name[count.index]
  timeout                       = var.timeout
  entry_point                   = var.functions[count.index]
  runtime                       = var.runtime
  service_account_email         = var.service_account_email
  ingress_settings              = var.ingress_settings

  environment_variables = {
    SECURITY_PROJECT    = var.project
    APP_ENVIRONMENT     = local.env
    APP_NAME            = var.name
  }

  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = "projects/${var.project}/topics/${var.pubsub_topic}"
  }
}
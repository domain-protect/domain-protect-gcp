# Dummy resource to ensure archive is created at apply stage
resource "null_resource" "dummy_trigger" {
  triggers = {
    timestamp = timestamp()
  }
}

# zip source code
data "archive_file" "code" {
  count       = length(var.functions)
  type        = "zip"
  source_dir  = "${path.module}/code/${var.functions[count.index]}"
  output_path = "${path.module}/build/${var.functions[count.index]}.zip"
  depends_on = [
    # Make sure archive is created in apply stage
    null_resource.dummy_trigger
  ]
}

# upload compressed code to bucket
resource "google_storage_bucket_object" "function" {
  count  = length(var.functions)
  name   = "${var.functions[count.index]}-${data.archive_file.code.*.output_md5[count.index]}.zip"
  bucket = var.bucket_name
  source = "${path.module}/build/${var.functions[count.index]}.zip"
}

resource "google_cloudfunctions2_function" "function" {
  count       = length(var.functions)
  name        = "${var.name}-${var.functions[count.index]}-${local.env}"
  location    = var.region
  description = "${var.name} ${var.functions[count.index]} function in ${local.env} environment"

  build_config {
    runtime     = var.runtime
    entry_point = var.functions[count.index]

    source {
      storage_source {
        bucket = var.bucket_name
        object = google_storage_bucket_object.function.*.name[count.index]
      }
    }
  }

  service_config {
    available_memory = "${var.available_memory}M"
    timeout_seconds  = var.timeout
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

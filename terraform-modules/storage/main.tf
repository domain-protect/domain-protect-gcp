# create storage bucket to store function code

resource "random_string" "value" {
  length    = 5
  special   = false
  min_lower = 5
}

resource "google_storage_bucket" "function_bucket" {
  name = "${var.name}-${local.env}-${random_string.value.result}"

  #checkov:skip=CKV_GCP_62: logging not needed for S3 bucket used for function code

  location                    = var.region
  force_destroy               = true
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }
}
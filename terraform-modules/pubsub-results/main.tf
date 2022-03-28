# pubsub topic to trigger functions
resource "google_pubsub_topic" "results" {
  name = "${var.name}-results-${local.env}"

  #checkov:skip=CKV_GCP_83: not opting to use KMS-based encryption key
}

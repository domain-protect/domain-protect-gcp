# pubsub topic to trigger functions
resource "google_pubsub_topic" "results" {
  name = "${var.name}-results-${local.env}"
}

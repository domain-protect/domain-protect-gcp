# pubsub topic to trigger functions
resource "google_pubsub_topic" "projects" {
  name = "${var.name}-projects-${local.env}"
}

# enable apis if needed
# requires serviceusage.googleapis.com to be enabled using console or gcloud
resource "google_project_service" "cloud_scheduler" {
  service            = "cloudscheduler.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "app_engine" {
  service            = "appengine.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "cloud_functions" {
  service            = "cloudfunctions.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "iam" {
  service            = "iam.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "cloud_build" {
  service            = "cloudbuild.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "secret_manager" {
  service            = "secretmanager.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "cloud_run" {
  service            = "run.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "event_arc" {
  service            = "eventarc.googleapis.com"
  disable_on_destroy = false
}

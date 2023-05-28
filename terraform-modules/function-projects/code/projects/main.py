#!/usr/bin/env python

import json
import os

import google.cloud.resourcemanager_v3

from google.cloud import pubsub_v1


def get_organization_id():
    # Gets organization ID - service account must only have rights to a single org
    # Requires Organization Viewer role at Organization level
    organizations_client = google.cloud.resourcemanager_v3.OrganizationsClient()
    orgs = organizations_client.search_organizations()
    for org in orgs:
        return org.name

    return ""


def list_folders(parent_id):
    # Lists folders under a parent - requires Folder Viewer role at Organization level
    folders_client = google.cloud.resourcemanager_v3.FoldersClient()
    folders = folders_client.list_folders(parent=parent_id)
    folder_list = [f.name for f in folders]

    return folder_list


def list_projects(parent_id):
    # Lists projects under a parent - requires Folder Viewer role at Organization level
    projects_client = google.cloud.resourcemanager_v3.ProjectsClient()
    projects = projects_client.list_projects(parent=parent_id)
    project_list = [p.project_id for p in projects if not p.project_id.startswith("sys-")]

    return project_list


def projects(event, context):  # pylint:disable=unused-argument
    security_project = os.environ["SECURITY_PROJECT"]
    app_name = os.environ["APP_NAME"]
    app_environment = os.environ["APP_ENVIRONMENT"]

    # Get organization ID
    org_id = get_organization_id()

    # Get all the project IDs at the organization level
    all_projects = list_projects(org_id)

    # Now retrieve all the folders directly under the organization
    folder_ids = list_folders(org_id)

    # Make sure that there are actually folders under the org
    if len(folder_ids) > 0:

        # Start iterating over the folders
        while folder_ids:
            # Get the last folder of the list
            current_id = folder_ids.pop()

            # Get subfolders and add them to the list of folders
            subfolders = list_folders(current_id)

            if subfolders:
                folder_ids.extend(f for f in subfolders)

            # Get the projects under that folder
            projects_under_folder = list_projects(current_id)

            # Add projects if there are any
            if projects_under_folder:
                all_projects.extend(p for p in projects_under_folder)

    print(f"Found {len(all_projects)} Projects in Organization")

    if len(all_projects) > 0:
        try:
            publisher = pubsub_v1.PublisherClient()
            topic_name = f"projects/{security_project}/topics/{app_name}-projects-{app_environment}"
            data = json.dumps({"Projects": all_projects})
            future = publisher.publish(topic_name, data=data.encode("utf-8"))
            print(f"Message ID {future.result()} published to topic {topic_name}")

        except google.api_core.exceptions.Forbidden:
            print(f"ERROR: Unable to publish to PubSub topic {topic_name}")

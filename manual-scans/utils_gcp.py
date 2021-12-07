from google.cloud.resourcemanager_v3 import (
    FoldersClient,
    OrganizationsClient,
    ProjectsClient,
)


def get_organization_id():
    # Gets organization ID - service account must only have rights to a single org
    # Requires Organization Viewer role at Organization level
    organizations_client = OrganizationsClient()
    orgs = organizations_client.search_organizations()
    for org in orgs:
        return org.name

    return ""


def list_folders(parent_id):
    # Lists folders under a parent - requires Folder Viewer role at Organization level
    folders_client = FoldersClient()
    folders = folders_client.list_folders(parent=parent_id)
    folder_list = [f.name for f in folders]

    return folder_list


def list_projects(parent_id):
    # Lists projects under a parent - requires Folder Viewer role at Organization level
    projects_client = ProjectsClient()
    projects = projects_client.list_projects(parent=parent_id)
    project_list = [
        p.project_id for p in projects if not p.project_id.startswith("sys-")
    ]

    return project_list


def list_all_projects():
    # Get organization ID
    org_id = get_organization_id()

    # Get all the project IDs at the organization level
    all_projects = list_projects(org_id)

    # Now retrieve all the folders directly under the organization
    folder_ids = list_folders(org_id)

    # Make sure that there are actually folders under the org
    if len(folder_ids) == 0:
        return all_projects

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

    # Finally, return all the projects
    return all_projects

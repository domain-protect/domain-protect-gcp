import asyncio
from google.cloud.resourcemanager_v3 import (
    FoldersAsyncClient,
    OrganizationsClient,
    ProjectsAsyncClient,
)


def get_organization_id():
    # Gets organization ID - service account must only have rights to a single org
    # Requires Organization Viewer role at Organization level
    organizations_client = OrganizationsClient()
    orgs = organizations_client.search_organizations()
    for org in orgs:
        return org.name

    return ""


async def list_all_projects():
    async def list_projects(parent_id):
        # Lists projects under a parent - requires Folder Viewer role at Organization level
        async for project in await project_client.list_projects(parent=parent_id):
            if project.project_id[:4] != "sys-":
                all_projects.append(project.project_id)
        return

    async def list_folders(parent_id):
        project_task = asyncio.create_task(list_projects(parent_id))
        folder_tasks = []
        # Lists folders under a parent - requires Folder Viewer role at Organization level
        async for folder in await folder_client.list_folders(parent=parent_id):
            folder_tasks.append(asyncio.create_task(list_folders(folder.name)))
        if project_task is not None:
            await project_task
        return await asyncio.gather(*folder_tasks)

    # Create Async Project and Folder Clients
    project_client = ProjectsAsyncClient()
    folder_client = FoldersAsyncClient()

    all_projects = []

    org_id = get_organization_id()
    await list_folders(org_id)

    return all_projects

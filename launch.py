from .project_reader import Project

reader = ProjectReader()
projects = reader.get_projects()
for key, project in projects.items():
    globals()[key] = project

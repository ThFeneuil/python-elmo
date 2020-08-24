from project_base import SimulationProject
import os, re
import inspect

PROJECTS_REPOSITORY = 'projects'

class ProjectReader:
    def __init__(self):
        pass
    
    def get_projects(self):
        projects = {}
        
        for root, repositories, files in os.walk(PROJECTS_REPOSITORY):
            for filename in files:
                if re.fullmatch(r'.*project.*\.py', filename):
                    # Encapsulation the project
                    complete_filename = root+'/'+filename
                    globals = {
                        #'__builtins__': {'__build_class__': __build_class__},
                        'SimulationProject': SimulationProject,
                    }
                    locals = {}
                    
                    # Read the project code
                    with open(complete_filename, 'r') as _file:
                        project = '\n'.join(_file.readlines())
                        exec(project, globals, locals)
                    
                    # Extract the simulations
                    for key, obj in locals.item():
                        if inspect.isclass(obj) and issubclass(obj, SimulationProject):
                            if key in projects:
                                print('Warning! Multiplie simulation with the same name. Simulation ignored: {} in {}'.format(key, complete_filename[len(PROJECTS_REPOSITORY)+1:]))
                            else:
                                obj.set_project_directory(root[len(PROJECTS_REPOSITORY)+1:])
                                projects[key] = obj
        
        return projects
        
    def get_project_classes(self):
        return self.get_projects().values()

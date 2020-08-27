import os, shutil
import re
import inspect
import subprocess

def search_simulations_in_repository(repository, criteria=lambda x:True):
    """ To search simulation classes in the 'repository' verifying the 'criteria' """
    projects = {}
    
    from .project_base import SimulationProject, write
    for root, repositories, files in os.walk(repository):
        for filename in files:
            if re.fullmatch(r'.*project.*\.py', filename):
                # Encapsulation the project
                complete_filename = root+'/'+filename
                globals = {
                    #'__builtins__': {'__build_class__': __build_class__},
                    'SimulationProject': SimulationProject,
                    'write': write,
                }
                locals = {}
                
                # Read the project code
                with open(complete_filename, 'r') as _file:
                    project = '\n'.join(_file.readlines())
                    exec(project, globals, locals)
                
                # Extract the simulations
                for key, obj in locals.items():
                    if inspect.isclass(obj) and issubclass(obj, SimulationProject):
                        if criteria(obj):
                            if key in projects:
                                print('Warning! Multiplie simulation with the same name. Simulation ignored: {} in {}'.format(key, complete_filename[len(repository)+1:]))
                            else:
                                obj.set_project_directory(os.path.abspath(root))
                                projects[key] = obj
    
    return projects

def search_simulations_in_module(criteria=lambda x:True):
    module_path = os.path.dirname(os.path.abspath(__file__))
    projects_path = module_path+'/projects'
    return search_simulations_in_repository(projects_path, criteria)

def search_simulations(repository, criteria=lambda x:True):
    projects = search_simulations_in_repository(repositories, criteria)

    module_projects = search_simulations_in_module
    for key, project in module_projects.items():
        if key not in projects:
            projects[key] = project

    return projects

class SimulationNotFoundError(Exception):
    pass
    
class TooManySimulationsError(Exception):
    pass
    
def get_simulation(repository, classname=None):
    """ Get a simulation class in the 'repository' with the specific 'classname' """
    criteria = lambda x: True
    if classname is not None:
        criteria = lambda x: x.__name__ == classname.strip()    
    projects = search_simulations(repository, criteria)
    
    if len(projects) == 1:
        return list(projects.values())[0]
    elif len(projects) < 1:
        raise SimulationNotFoundError()
    else:
        raise TooManySimulationsError()
        
def get_simulation_via_classname(classname):
    return get_simulation('.', classname)
        
def create_simulation(repository, classname):
    """ Create a simulation class """
    try:
        os.makedirs(repository, exist_ok=False)
    except FileExistsError as err:
        raise FileExistsError('Error, a project with this repository already exists!') from err
        
    module_path = os.path.dirname(os.path.abspath(__file__))
    elmo_path = module_path+'/elmo'
    template_path = module_path+'/templates'
    project_path = repository

    ### Add contents in the project
    files_from_ELMO = [
        'Examples/elmoasmfunctions.o',
        'Examples/elmoasmfunctions.s',
        'Examples/elmoasmfunctionsdef.h',
        'Examples/DPATraces/MBedAES/vector.o',
    ]
    files_from_templates = [
        'elmoasmfunctionsdef-extension.h',
        'Makefile',
        'project.c'
    ]

    for filename in files_from_ELMO:
        shutil.copy(elmo_path+'/'+filename, project_path)
    for filename in files_from_templates:
        shutil.copy(template_path+'/'+filename, project_path)
    shutil.copy(elmo_path+'/'+'Examples/DPATraces/MBedAES/MBedAES.ld', project_path+'/'+'project.ld')

    ### Create the project class
    with open(template_path+'/projectclass.py') as _source:
        code = ''.join(_source.readlines())
        code = code.replace('{{PROJECTCLASSNAME}}', classname)
        with open(project_path+'/'+'projectclass.py', 'w') as _dest:
            _dest.write(code)
            
    return os.path.abspath(project_path)

def execute_simulation(project, data=None):
    """ Execute a simulation with 'data' """
    # Make the compilation
    if False:
        print('Compiling binary...')
        
        # Adapt the project source
        with open('binaries/Frodo/frodo-base.c', 'r') as _src_file:
            content = _src_file.read()
            with open('binaries/Frodo/frodo.c', 'w') as _dst_file:
                _dst_file.write(content.replace('%NEED_TO_FILL%', str(n)))
        
        # Compile the project
        make_directory = 'projects/{}/{}'.format(project.get_project_directory(), project.get_make_directory())
        process = subprocess.Popen('make', shell=True, cwd=make_directory, executable='/bin/bash', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        if error and ('error' in error.decode('latin-1')):
            print("Error to compile")
            print(error)
            raise Exception()
        
        # Save last compilation data
        global_variables[project_name] = {
            'last_n': n,
        }
    
    # Generate the trace by launching ELMO
    command = './elmo {}/{}'.format(
        project.get_project_directory(),
        project.get_binary()
    )
    cwd = os.path.dirname(os.path.abspath(__file__))+'/elmo'
    process = subprocess.Popen(command, shell=True, cwd=cwd, executable='/bin/bash', stdout=subprocess.PIPE)
    output, error = process.communicate()

    # Return results
    return (
        output.decode('latin-1') if output else None,
        error.decode('latin-1') if error else None,
    )
    
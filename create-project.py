import os, shutil
import re

print('Creation of a new simulation project...')

### Create the repository of the projects
global_path = 'projects'
os.makedirs(global_path, exist_ok=True)

### Get the project classname
project_classname = ''
search = re.compile(r'[^a-zA-Z0-9_]').search
while not project_classname:
    classname = input(' - What is the project classname? ')
    if search(classname):
        print('   > Illegal characters detected! Please enter a name with only the following characters : a-z, A-Z, 0-9, and "_".')
    else:
        project_classname = classname.strip()

### Get and create the project repository
search = re.compile(r'[^a-zA-Z0-9.-_/]').search
project_repository = ''
while not project_repository:
    repository = input(' - What is the project repository? ')
    if search(repository):
        print('Illegal characters detected! Please enter a name with only the following characters : a-z, A-Z, 0-9, ".", "-", "_" and "/".')
    else:
        try:
            os.makedirs(global_path+'/'+repository, exist_ok=False)
            project_repository = repository
        except FileExistsError:
            print('Error, a project with this repository already exists!')
project_path = global_path+'/'+repository

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
    shutil.copy('elmo/'+filename, project_path)
for filename in files_from_templates:
    shutil.copy('templates/'+filename, project_path)
shutil.copy('elmo/'+'Examples/DPATraces/MBedAES/MBedAES.ld', project_path+'/'+'project.ld')

### Create the project class
with open('templates/projectclass.py') as _source:
    code = ''.join(_source.readlines())
    code = code.replace('{{PROJECTCLASSNAME}}', project_classname)
    with open(project_path+'/'+'projectclass.py', 'w') as _dest:
        _dest.write(code)

print('')
print('Creation complete !')
print(' - Project repository: {}'.format(os.path.abspath(project_path)))
print(' - Project class "{}" in {}'.format(project_classname, os.path.abspath(project_path+'/'+'projectclass.py')))
print(' - Linker script: {}'.format(os.path.abspath(project_path+'/'+'project.ld')))
print('')
print('Please don\'t to compile the project with the present Makefile before using it!')

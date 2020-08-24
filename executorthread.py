from servicethread import OneShotServiceThread
import subprocess

import shutil
from project_reader import ProjectReader

global_variables = {}

class ExecutorThread(OneShotServiceThread):
    def __init__(self, ip, port, clientsocket, **kwargs):
        super().__init__(ip, port, clientsocket)
        self.projects = kwargs['projects'] if 'projects' in kwargs else None

    def execute(self):
        projects = self.projects
        if project is None:
            reader = ProjectReader()
            projects = {sc.get_project_label(): sc for sc in reader.get_project_classes()}
            print('Warning: need to research the projects.')
        else:
            print('Already have projects')
        
        data = self.protocol.get_data()
        self.protocol.please_assert(data)
        self.protocol.please_assert('project' in data)
        self.protocol.please_assert(data['project'] in projects)
        self.protocol.send_ack()

        # Get the project
        project = projects[data['project']]
        
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
        command = './elmo ../projects/{}/{}'.format(project.get_project_directory(), project.get_binary())
        process = subprocess.Popen(command, shell=True, cwd='elmo_online/elmo/', executable='/bin/bash', stdout=subprocess.PIPE)
        output, error = process.communicate()

        # Send results
        self.protocol.send_data({
            'output': output.decode('latin-1') if output else None,
            'error': error.decode('latin-1') if error else None,
        })
        self.protocol.close()

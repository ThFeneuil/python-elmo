from .server.servicethread import OneShotServiceThread
import subprocess

import shutil

import os, re

class ExecutorThread(OneShotServiceThread):
    def __init__(self, ip, port, clientsocket, **kwargs):
        super().__init__(ip, port, clientsocket)

    def execute(self):
        data = self.protocol.get_data()
        self.protocol.please_assert(data)
        
        # Set the input of ELMO
        self.protocol.please_assert('input' in data)
        with open('elmo/input.txt', 'w') as _input_file:
            _input_file.write(data['input'])
        
        self.protocol.send_ack()
        
        # Get the binary
        binary_content = self.protocol.get_file()
        with open('elmo/project.bin', 'wb') as _binary_file:
            _binary_file.write(binary_content)
                
        ### Generate the traces by launching ELMO
        command = './elmo ./project.bin'
        cwd = './elmo/'
        process = subprocess.Popen(
            command, shell=True, cwd=cwd,
            executable='/bin/bash',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output, error = process.communicate()
        output = output.decode('latin-1') if output else None
        error = error.decode('latin-1') if error else None
        
        if error:
            self.protocol.send_data({
                'output': output,
                'error': error,
            })
            self.protocol.close()
            return
        
        ### Get traces
        nb_traces = output.count('TRACE NO')

        trace_filenames = []
        for filename in os.listdir('elmo/output/traces/'):
            if len(trace_filenames) < nb_traces:
                if re.search(r'^trace\d+\.trc$', filename):
                    trace_filenames.append('elmo/output/traces/{}'.format(filename))
            else:
                break
        
        assert len(trace_filenames) == nb_traces
        results = trace_filenames
        
        for i in range(len(results)):
            with open(results[i], 'r') as _file:
                results[i] = list(map(float,  _file.readlines()))
                
        ### Get asmtrace and printed data
        asmtrace = None
        if not ('asmtrace' in data and not data['asmtrace']):
            with open('elmo/output/asmoutput/asmtrace00001.txt', 'r') as _file:
                asmtrace = ''.join(_file.readlines())

        printed_data = None
        if not ('printdata' in data and not data['printdata']):
            with open('elmo/output/printdata.txt', 'r') as _file:
                printed_data = list(map(lambda x: int(x, 16), _file.readlines()))

        ### Send results
        self.protocol.send_data({
            'output': output,
            'error': error,
            'nb_traces': nb_traces,
            'results': results,
            'asmtrace': asmtrace,
            'printed_data': printed_data,
        })
        self.protocol.close()

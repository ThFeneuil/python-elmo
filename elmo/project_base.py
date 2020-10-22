import os, re
import numpy as np
from os.path import join as pjoin

from .config import (
    MODULE_PATH,
    ELMO_TOOL_REPOSITORY,
    ELMO_INPUT_FILE_NAME,
    DEFAULT_HOST,
    DEFAULT_PORT,
)
from .utils import write

class SimulationProject:
    # TAG: EXCLUDE-FROM-SIMULATION-SEARCH
    """ Class to manage a simultion
    It contains all the parameters of the simulation and has method to use it
    """
    _nb_bits_for_nb_challenges = 16
    _project_directory = None
    
    ### Define the project
    @classmethod
    def get_project_directory(cl):
        """ """
        if cl._project_directory:
            return cl._project_directory
        else:
            raise NotImplementedError()
    
    @classmethod
    def set_project_directory(cl, project_directory):
        cl._project_directory = project_directory

    @classmethod
    def get_project_label(cl):
        return cl.get_project_directory()

    @classmethod
    def get_make_directory(cl):
        return ''
        
    @classmethod
    def get_binary_path(cl):
        raise NotImplementedError()
        
    @classmethod
    def get_parameters_names(cl):
        return set()
        
    def get_challenge_format(self):
        raise NotImplementedError()


    ### Tools to realize the simulation of the project
    def __init__(self, challenges=None):
        self.elmo_folder = pjoin(MODULE_PATH, ELMO_TOOL_REPOSITORY)
        self.challenges = challenges
        self.reset()
        
    def reset(self):
        self.is_executed = False
        self.has_been_online = False

        self._nb_traces = None
        self._complete_asmtrace = None
        self._complete_results = None
        self._complete_printed_data = None
    
    def get_test_challenges(self):
        raise NotImplementedError()

    def get_random_challenges(self, nb_challenges):
        raise NotImplementedError()
    
    def set_challenges(self, challenges):
        self.reset()
        self.challenges = challenges

    def get_input_filename(self):
        return pjoin(self.elmo_folder, ELMO_INPUT_FILE_NAME)

    def get_printed_data_filename(self):
        return pjoin(self.elmo_folder, 'output', 'printdata.txt')

    def get_asmtrace_filename(self):
        return pjoin(self.elmo_folder, 'output', 'asmoutput', 'asmtrace00001.txt')
    
    def set_input_for_each_challenge(self, input, challenge):
        format = self.get_challenge_format()

        def aux(sizes, data):
            if len(sizes) == 0:
                write(input, data)
            else:
                assert len(data) == sizes[0], 'Incorrect format for challenge. Get {} instead of {}'.format(len(data), sizes[0])
                for i in range(sizes[0]):
                    aux(sizes[1:], data[i])

        for num_part in range(len(format)):                
            aux(format[num_part], challenge[num_part])

    def set_input(self, input):
        if self.challenges:
            assert len(self.challenges) < (1 << self._nb_bits_for_nb_challenges), \
                'The number of challenges must be strictly lower than {}. Currently, there are {} challenges.'.format(
                    1 << self._nb_bits_for_nb_challenges,
                    len(self.challenges),
                )
            write(input, len(self.challenges), nb_bits=self._nb_bits_for_nb_challenges)
            for challenge in self.challenges:
                self.set_input_for_each_challenge(input, challenge)
            
    def run(self):
        self.reset()
        with open(self.get_input_filename(), 'w') as _input:
            self.set_input(_input)
            
        from .manage import execute_simulation
        res = execute_simulation(self)
        
        self.is_executed = True
        self.has_been_online = False
        self._nb_traces = res['nb_traces']
        return res
        
    def run_online(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        from .server.protocol import SocketTool
        import socket

        class TempInput:
            def __init__(self):
                self._buffer = ''
            def write(self, data):
                self._buffer += data
            def get_string(self):
                return self._buffer
        
        self.reset()
        input = TempInput()
        self.set_input(input)
        
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
            SocketTool.send_data(s, {
                'input': input.get_string(),
            })
            if not SocketTool.get_ack(s):
                raise RuntimeError("NACK received: The request has been refused!")
            
            SocketTool.send_file(s, '{}/{}'.format(self.get_project_directory(), self.get_binary_path()))
            if not SocketTool.get_ack(s):
                raise RuntimeError("NACK received: The binary file has been refused!")
            
            data = SocketTool.get_data(s)
            if data['error']:
                raise Exception("The simulation returned an error: {}".format(data['error']))
            s.close()
        except IOError as err:
            raise RuntimeError("The connection refused. Has the ELMO server been switch on?") from err
            
        self.is_executed = True
        self.has_been_online = True
        self._nb_traces = data['nb_traces']
        self._complete_asmtrace = data['asmtrace']
        self._complete_results = data['results']
        self._complete_printed_data = data['printed_data']
        return { key: value
            for key, value in data.items()
            if key not in ['results', 'asmtrace', 'printed_data']
        }
        
    ### Manipulate the results
    def get_number_of_challenges(self):
        return len(self.challenges)
        
    def get_number_of_traces(self):
        assert self.is_executed
        return self._nb_traces
    
    def get_results_filenames(self):
        assert self.is_executed
        assert not self.has_been_online
        nb_traces = self.get_number_of_traces()
        output_path = os.path.join(self.elmo_folder, 'output')
        
        filenames = []
        for i in range(nb_traces):
            filename = os.path.join(output_path, 'traces', 'trace%05d.trc' % (i+1))
            assert os.path.isfile(filename)
            filenames.append(filename)
        
        return filenames            
    
    def get_results(self):
        """
        Warning: The output list is the same object stored in the instance.
            If you change this object, it will change in the instance too, and the
            next call to 'get_results' will return the changed object.
        """
        assert self.is_executed
        nb_traces = self.get_number_of_traces()

        # Load the power traces
        if self._complete_results is None:
            self._complete_results = []
            for filename in self.get_results_filenames():
                with open(filename, 'r') as _file:
                    self._complete_results.append(list(map(float,  _file.readlines())))

        return self._complete_results
    
    def get_traces(self, indexes=None):
        """
        """
        assert self.is_executed
        results = self.get_results()

        nb_traces = self.get_number_of_traces()
        trace_length = len(results[0])
        
        if indexes is None:
            traces = np.zeros((nb_traces, trace_length))
            for i in range(nb_traces):
                traces[i,:] = results[i]
            return traces
        
        else:
            traces = np.zeros((nb_traces, len(indexes)))
            for i in range(nb_traces):
                traces[i,:] = results[i][indexes]
            return traces

    ### Manipulate the ASM trace
    def get_asmtrace(self):
        """ Get the ASM trace of the last simulation
        The ASM trace is the list of the leaking assembler instructions,
            one instruction each point of the leakage power trace
        """
        assert self.is_executed
        
        # Load the ASM trace
        if self._complete_asmtrace is None:
            with open(self.get_asmtrace_filename(), 'r') as _file:
                self._complete_asmtrace = _file.read()        
        if type(self._complete_asmtrace):
            self._complete_asmtrace = self._complete_asmtrace.split('\n')   
        
        return self._complete_asmtrace 
    
    def get_indexes_of(self, condition):
        """ Get the list of indexes of the instructions
        verifying the 'condition' in the ASM trace
        :condition: Boolean function with ASM instruction (string) for input
        """
        assert self.is_executed
        return [i for i, instr in enumerate(self.get_asmtrace()) if condition(instr)]

    ### Manipulate the Printed Data
    def get_printed_data(self, per_trace=True):
        """ Get the printed data of the last simulation
        A printed data is a data which has been given to the function 'printbyte'
            during the simulation
        :per_trace: If True (default), split equally the printed data in a table
            with a length equal to the number of simulated power traces
        """
        assert self.is_executed
        
        # Load the printed data
        if self._complete_printed_data is None:
            with open(self.get_printed_data_filename(), 'r') as _file:
                self._complete_printed_data = list(map(lambda x: int(x, 16), _file.readlines()))
        
        if per_trace:
            # Return printed data for each trace
            data = self._complete_printed_data
            nb_traces = self.get_number_of_traces()
            nb_data_per_trace = len(data) // nb_traces
        
            return [data[nb_data_per_trace*i:nb_data_per_trace*(i+1)] for i in range(nb_traces)]        
        
        else:
            # Return printed data
            return self._complete_printed_data

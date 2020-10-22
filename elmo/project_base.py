import os, re
import numpy as np

from .config import MODULE_PATH, ELMO_TOOL_REPOSITORY
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
        self.elmo_folder = os.path.join(MODULE_PATH, ELMO_TOOL_REPOSITORY)
        self.challenges = challenges
        self.reset()
        
    def reset(self):
        self.is_executed = False
        self.has_been_online = False

        self._complete_asmtrace = None
        self._complete_results = None
        self._complete_printed_data = None
    
    def get_test_challenges(self):
        raise NotImplementedError()

    def get_random_challenges(self, nb_challenges):
        raise NotImplementedError()
    
    def set_challenges(self, challenges):
        self.challenges = challenges

    def get_writable_input_file(self):
        return open('{}/input.txt'.format(self.elmo_folder), 'w')

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
        with open('{}/input.txt'.format(self.elmo_folder), 'w') as _input:
            self.set_input(_input)
        from .manage import execute_simulation
        res = execute_simulation(self)
        self.is_executed = True
        self.has_been_online = False
        return res
        
    def run_online(self, host='localhost', port=5000):
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
        self._complete_asmtrace = data['asmtrace']
        self._complete_results = data['results']
        self._complete_printed_data = data['printed_data']
        return { key: value
            for key, value in data.items()
            if key not in ['results', 'asmtrace', 'printed_data']
        }
        
    ### Manipulate the ASM trace
    def get_asmtrace_filename(self):
        return '{}/output/asmoutput/asmtrace00001.txt'.format(self.elmo_folder)
    
    def get_asmtrace(self):
        if self._complete_asmtrace is None:
            with open(self.get_asmtrace_filename(), 'r') as _file:
                self._complete_asmtrace = ''.join(_file.readlines())
        
        return self._complete_asmtrace.split('\n')        
    
    def get_indexes_of(self, condition):
        return [i for i, instr in enumerate(self.get_asmtrace()) if condition(instr)]

    ### Manipulate the results
    def get_number_of_traces(self):
        return len(self.challenges)
    
    def get_results(self, only_filenames=False, reorganise=None, indexes=None):
        assert self.is_executed
        nb_traces = self.get_number_of_traces()

        if only_filenames and self.has_been_online:
            raise Exception('Impossible to get the filenames for an online execution')

        if only_filenames or self._complete_results is None:
            trace_filenames = []
            for filename in os.listdir('{}/output/traces/'.format(self.elmo_folder)):
                if re.search(r'^trace\d+\.trc$', filename):
                    trace_filenames.append('{}/output/traces/{}'.format(self.elmo_folder, filename))
                    if len(trace_filenames) >= nb_traces:
                        break
            
            assert len(trace_filenames) == nb_traces
            if only_filenames:
                return reorganise(trace_filenames) if reorganise is not None else trace_filenames

            self._complete_results = []
            for filename in trace_filenames:
                with open(filename, 'r') as _file:
                    self._complete_results.append(list(map(float,  _file.readlines())))

        results = self._complete_results
        if indexes is not None:
            for i in range(len(self._complete_results)):
                results[i] = results[i][indexes]

        if reorganise is not None:
            results = reorganise(results)
        return results
    
    def get_traces(self, reorganise=None, indexes=None):
        results = self.get_results(only_filenames=False, reorganise=reorganise, indexes=indexes)

        nb_traces = self.get_number_of_traces()
        trace_length = len(results[0])

        traces = np.zeros((nb_traces, trace_length))
        for i in range(nb_traces):
            traces[i,:] = results[i]
        
        if reorganise is not None:
            traces = reorganise(traces)
        
        return traces

    ### Manipulate the Printed Data
    def get_printed_data(self):
        if self._complete_printed_data is None:
            with open('{}/output/printdata.txt'.format(self.elmo_folder), 'r') as _file:
                self._complete_printed_data = list(map(lambda x: int(x, 16), _file.readlines()))
        
        data = self._complete_printed_data
        nb_traces = self.get_number_of_traces()
        nb_data_per_trace = len(data) // nb_traces
        
        return [data[nb_data_per_trace*i:nb_data_per_trace*(i+1)] for i in range(nb_traces)]        
        
    ### Other
    def analyse_operands(self, num_line, num_trace=1):
        num_str = str(num_trace)
        num_str = '0'*(5-len(num_str)) + num_str
        
        operands_filename = self.elmo_folder + '/output/operands/operands{}.txt'.format(num_str)
        trace_filename = self.elmo_folder + '/output/traces/trace0000{}.trc'.format(num_trace)
        
        is_multiple = (type(num_line) is list)
        if not is_multiple:
            num_line = [num_line]
        output = [{}]*len(num_line)
        
        with open(operands_filename, 'r') as _file:
            lines = _file.readlines()
            for i, num in enumerate(num_line):
                line = lines[num].split()
                data = list(map(int, line[0:7]))
                output[i]['previous'] = data[0:2]
                output[i]['current'] = data[2:4]
                output[i]['triplet'] = data[4:7]
                output[i]['other'] = list(map(float, line[7:]))
        
        with open(trace_filename, 'r') as _file:
            lines = _file.readlines()
            for i, num in enumerate(num_line):
                line = lines[num]
                output[i]['power'] = float(line)
            
        return output if is_multiple else output[0]


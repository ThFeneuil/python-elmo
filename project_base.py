import os, re
import socket
from protocol import SocketTool
import numpy as np

def to_hex(v, nb_bits=16):
    try:
        v_hex = v.hex()
    except AttributeError:
        v_hex = hex(v)[2:]
    return '0'*(nb_bits//4-len(v_hex)) + v_hex

def split_octet(hexstr):
    return [hexstr[i:i+2] for i in range(0, len(hexstr), 2)]

def to_signed_hex(v, nb_bits=16):
    return split_octet(to_hex(v & (2**nb_bits-1), nb_bits=nb_bits))

def write(_input, uintXX, nb_bits=16):
    uintXX = to_signed_hex(uintXX, nb_bits=nb_bits)
    for i in range(nb_bits//8):
        _input.write(uintXX[i]+'\n')
    
def write_list(_input, uint16_list):
    for uint16 in uint16_list:
        write(_input, uint16)

def launch_simulation(quiet=False, **kwargs):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('localhost', 5000))
        SocketTool.send_data(s, kwargs)
        if not SocketTool.get_ack(s):
            raise RuntimeError("The request has been refused !")
        else:
            data = SocketTool.get_data(s)
            if data['error'] and not quiet:
                raise Exception("The simulation return an error")
            return data['output'], data['error']
        s.close()
    except IOError:
        raise RuntimeError("The connection refused. Has the ELMO server been switch on ?")


class SimulationProject:
    _nb_bits_for_nb_challenges = 16
    _project_directory = None
    
    ### Define the project
    @classmethod
    def get_project_directory(cl):
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
    def get_binary(cl):
        raise NotImplementedError()
        
    @classmethod
    def get_parameters_names(cl):
        return set()
        
    @classmethod
    def adapt_project(cl, parameters):
        return
        
    def get_challenge_format(self):
        raise NotImplementedError()


    ### Tools to realize the simulation of the project
    def __init__(self, challenges=None):
        self.elmo_folder = os.path.dirname(os.path.abspath(__file__))+'/elmo'
        self.challenges = challenges
        self.is_executed = False
    
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
        assert len(self.challenges) < 2**16, 'The number of challenges must be strictly lower than 65536. Currently, there are {} challenges.'.format(len(self.challenges))
        write(input, len(self.challenges), nb_bits=self._nb_bits_for_nb_challenges)
        for challenge in self.challenges:
            self.set_input_for_each_challenge(input, challenge)
            
    def run(self):
        with open('{}/input.txt'.format(self.elmo_folder), 'w') as _input:
            self.set_input(_input)
        launch_simulation(project=self.get_project_label(), quiet=False)
        self.is_executed = True
        
    def get_asmtrace_filename(self):
        return '{}/output/asmoutput/asmtrace00001.txt'.format(self.elmo_folder)
        
    def get_indexes_of(self, condition):
        with open(self.get_asmtrace_filename(), 'r') as _file:
            asmtrace = _file.readlines()
            return [i for i, instr in enumerate(asmtrace) if condition(instr)]
    
    def get_number_of_traces(self):
        return len(self.challenges)
    
    def get_results(self, only_filenames=False, reorganise=None, indexes=None):
        assert self.is_executed
        nb_traces = self.get_number_of_traces()

        trace_filenames = []
        for filename in os.listdir('{}/output/traces/'.format(self.elmo_folder)):
            if re.search(r'^trace\d+\.trc$', filename):
                trace_filenames.append('{}/output/traces/{}'.format(self.elmo_folder, filename))
                if len(trace_filenames) >= nb_traces:
                    break
        
        assert len(trace_filenames) == nb_traces
        results = trace_filenames
        
        if not only_filenames:
            for i in range(len(results)):
                with open(results[i], 'r') as _file:
                    if indexes is not None:
                        results[i] = list(map(float,  _file.readlines()[indexes]))
                    else:
                        results[i] = list(map(float,  _file.readlines()))

        if reorganise is not None:
            results = reorganise(results)

        return results
    
    def get_traces(self, reorganise=None, indexes=None):
        results = self.get_results(only_filenames=False, reorganise=reorganise,indexes=indexes)

        nb_traces = self.get_number_of_traces()
        trace_length = len(results[0])

        traces = np.zeros((nb_traces, trace_length))
        for i in range(nb_traces):
            traces[i,:] = results[i]
            
        if reorganise is not None:
            traces = reorganise(traces)
            
        return traces

    def get_printed_data(self):
        with open('{}/output/printdata.txt'.format(self.elmo_folder), 'r') as _file:
            data = list(map(lambda x: int(x, 16), _file.readlines()))
        
        nb_traces = self.get_number_of_traces()
        nb_data_per_trace = len(data) // nb_traces
        
        return [data[nb_data_per_trace*i:nb_data_per_trace*(i+1)] for i in range(nb_traces)]        
        
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


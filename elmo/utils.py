import numpy as np

### Binary operations
def hweight(n):
    c = 0
    while n>0:
        c += (n & 1)
        n >>= 1
    return c

def hdistance(x,y):
    return hweight(x^y)

def binary_writing(n, nb_bits=32, with_hamming=False):
    n = np.array(n)
    w, h = np.zeros((nb_bits, len(n))), np.zeros((len(n)))

    for ind in range(nb_bits):
        w[ind] = (n & 1)
        h += w[ind]

        n >>= 1
        ind += 1
    
    return (w, h) if with_hamming else w
    
### Conversion
def to_hex(v, nb_bits=16):
    try:
        v_hex = v.hex()
    except AttributeError:
        v_hex = hex(v)[2:]
    return '0'*(nb_bits//4-len(v_hex)) + v_hex

def split_octet(hexstr):
    return [hexstr[i:i+2] for i in range(0, len(hexstr), 2)]

def to_signed_hex(v, nb_bits=16):
    try:
        return split_octet(to_hex(v & ((1<<nb_bits)-1), nb_bits=nb_bits))
    except TypeError as err:
        raise TypeError('Error to transform a <{}> into signed hex.'.format(type(v))) from err

### Write function
def write(_input, uint, nb_bits=16):
    uint = to_signed_hex(uint, nb_bits=nb_bits)
    for i in range(nb_bits//8):
        _input.write(uint[i]+'\n')
    
def write_list(_input, uint_list, nb_bits=16):
    for uint in uint_list:
        write(_input, uint, nb_bits=nb_bits)

### Print Utils
class Color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

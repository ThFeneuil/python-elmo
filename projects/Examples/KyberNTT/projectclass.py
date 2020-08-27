### In this file is defined a Python class to manipulate the simualtion project.
###  - This class must be inherited from th class 'SimulationProject' (no need to import it)
###  - You can use here the function "write(input_file, uint, nb_bits=16)"
###            to write an integer of 'nb_bits' bits in the 'input_file' (no need to import it too).
### To get this simulation class in Python scripts, please use the functions in manage.py as
###  - search_simulations(repository)
###  - get_simulation(repository, classname=None)
###  - get_simulation_via_classname(classname)

class KyberNTTSimulation(SimulationProject):
    @classmethod
    def get_binary(cl):
        return 'project.bin'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_input(self, input):
        """ Write into the 'input' file of ELMO tool
                the parameters and the challenges for the simulation """
        super().set_input(input)

    def set_input_for_each_challenge(self, input, challenge):
        """ Write into the 'input' file of ELMO tool
                the 'challenge' for the simulation """
        secret = challenge

        # Write the secret vector
        for j in range(2): #k=2 for Kyber512
            for k in range(256): #n=256 for Kyber512
                write(input, secret[j,k])
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
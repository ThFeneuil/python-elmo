class {{PROJECTCLASSNAME}}(SimulationProject):
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
        super().set_input_for_each_challenge(input, challenge)

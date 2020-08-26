# Online ELMO

_Online ELMO_ is a Python library which proposes an encapsulation of the project _ELMO_.

[MOW17] **Towards Practical Tools for Side
Channel Aware Software Engineering : ’Grey Box’ Modelling for Instruction Leakages**
by _David McCann, Elisabeth Oswald et Carolyn Whitnall_.
https://www.usenix.org/conference/usenixsecurity17/technical-sessions/presentation/mccann

**ELMO GitHub**: https://github.com/sca-research/ELMO

## Requirements

To use _Online ELMO_, you need at least Python3.5 and the packages present in the file requirements.txt

```bash
pip3 install -r requirements.txt
```

The library will install and compile ELMO. So, you need the GCC compiler collection  and the command/utility 'make' (for more details, see the documentation of ELMO). On Ubuntu/Debian,

```bash
sudo apt install build-essential
```

To use ELMO on a leaking binary program, you need to compile the C implementations to binary programs (a ".bin" file). "ELMO is not linked to any ARM specific tools, so users should be fine to utilise whatever they want for this purpose. A minimal working platform for compiling your code into an ARM Thumb binary would be to use the GNU ARM Embedded Toolchain (tested version: arm-none-eabi-gcc version 7.3.1 20180622, it can be downloaded from https://developer.arm.com/open-source/gnu-toolchain/gnu-rm).", see the [documentation of ELMO](https://github.com/sca-research/ELMO) for more details.

## Installation

First, download _Online ELMO_.

```bash
git clone https://git.aprilas.fr/tfeneuil/OnlineELMO
```

And then, install ELMO thanks to the script of installation.

```bash
./install
```

## Usage

### Create a new simulation project

What is a _simulation project_ ? It is a project to simulate the traces of _one_ binary program. It includes
 - A Python class which enable to generate traces in Python;
 - The C program which will be compile to have the binary program for the analysis;
 - A linker script where the configuration of the simulated device are defined.

To start a new project, you can use the following function.

```python3
> from elmo_online.manage import create_simulation
> create_simulation(
>    'dilithium', # The (relative) path of the project
>    'DilithiumSimulation' # The classname of the simulation
>)
```

This function will create a repository _dilithium_ with all the complete squeleton of the project. In this repository, you can find:
 - The file _project.c_ where you must put the leaking code;
 - The file _projectclass.py_ where there is the class of the simulation which will enable you to generate traces of the project in Python scripts;
 - A _Makefile_ ready to be used with a compiler _arm-none-eabi-gcc_.
 
_Online ELMO_ offers a example project to you in the repository _projects/Examples_ in the module. This example is a project to generate traces of the execution of the NTT implemented in the cryptosystem [Kyber](https://pq-crystals.org/kyber/).

### List all the available simulation

```python3
>from elmo_online.manage import search_simulations
>search_simulations('.')
{'DilithiumSimulation': <class 'DilithiumSimulation'>,
 'KyberNTTSimulation': <class 'KyberNTTSimulation'>}
```

### Use a simulation project

Warning! Before using it, you have to compile your project thanks to the provided Makefile.

```python
> from elmo_online.manage import get_simulation
> KyberSimulation = get_simulation_via_classname('KyberNTTSimulation')
> 
> import numpy as np
> Kyber512 = {'k': 2, 'n': 256}
> challenges = [
>     np.ones((Kyber512['k'], Kyber512['n']), dtype=int),
> ]
> 
> simulation = KyberSimulation(challenges)
> simulation.run() # Launch the simulation
> traces = simulation.get_traces()
> # And now, I can draw and analyse the traces
```

### Use the ELMO Engine

The engine exploits the model of ELMO to directly give the power consumption of an assembler instruction. In the model, to have the power consumption of an assembler instruction, it needs
 - the type and the operands of the previous assembler instruction
 - the type and the operands of the current assembler instruction
 - the type of the next assembler instruction

The type of the instructions are:
 - "_**EOR**_" for ADD(1-4), AND, CMP, CPY, EOR, MOV, ORR, ROR, SUB;
 - "_**LSL**_" for LSL(2), LSR(2);
 - "_**STR**_" for STR, STRB, STRH;
 - "_**LDR**_" for LDR, LDRB, LDRH;
 - "_**MUL**_" for MUL;
 - "_**OTHER**_" for the other instructions.

```python
> from elmo_online.engine import ELMOEngine, Instr
> engine = ELMOEngine()
> for i in range(0, 256):
>     engine.add_point(
>         (Instr.LDR, Instr.MUL, Instr.OTHER), # Types of the previous, current and next instructions
>         (0x0000, i), # Operands of the previous instructions
>         (0x2BAC, i)  # Operands of the current instructions
>     )
> engine.run() # Compute the power consumption of all these points
> power = engine.power # Numpy 1D array with an entry for each previous point
> engine.reset_points() # Reset the engine to study other points
```

## Licences

[MIT](LICENCE.txt)

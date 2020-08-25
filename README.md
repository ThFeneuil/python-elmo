# Online ELMO

_Online ELMO_ is a Python library which proposes an encapsulation of the project _ELMO_.

[MOW17] **Towards Practical Tools for Side
Channel Aware Software Engineering : ’Grey Box’ Modelling for Instruction Leakages**
by _David McCann, Elisabeth Oswald et Carolyn Whitnall_.
https://www.usenix.org/conference/
usenixsecurity17/technical-sessions/presentation/mccann.

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

To use ELMO on a leaking binary program, you need to compile the C implementations to binary programs (a ".bin" file). "ELMO is not linked to any ARM specific tools, so users should be fine to utilise whatever they want for this purpose."

ELMO Documentation: "A minimal working platform for compiling your code into an ARM Thumb binary would be to use the GNU ARM Embedded Toolchain (tested version: arm-none-eabi-gcc version 7.3.1 20180622, it can be downloaded from https://developer.arm.com/open-source/gnu-toolchain/gnu-rm).", see the documentation for more details.

## Installation

First, download _ELMO Online_.

```bash
git clone https://git.aprilas.fr/tfeneuil/OnlineELMO
```

And then, install ELMO by launching the ELMO run_server (you must have GCC to compile ELMO, if it is not the case, please do "sudo apt install build-essential" on Ubuntu/Debian)

```bash
./run
```

## Usage

### Create a new simulation project

What is a _simulation project_ ? It is a project to simulate the traces of _one_ binary program. It includes
 - A Python class which enable to generate traces in Python ;
 - The C program which will be compile to have the binary program for the analysis ;
 - A linker script where the configuration of the simulated device are defined

```bash
python3 create-project.py
> Creation of a new simulation project...
>  - What is the project classname? KyberSimulation # Please enter here the name of the Python class of the simulation
>  - What is the project repository? Kyber/SimuOne # Please enter here the relative repository of the simulation
```

### Use a simulation project in a Python script

Warning! Before using it, you have to compile your project thanks to the provided Makefile.

```python
from elmo_online.launch import KyberSimulation
simulation = KyberSimulation(challenges)
simulation.run() # Launch the simulation
traces = simulation.get_traces()
# And now, I can analyse the traces
```

### Use the ELMO Engine

The engine use the model of ELMO to directly give the power consumption of an assembler instruction. In the model, to have the power consumption of an assembler instruction, it needs
 - the type and the operands of the previous assembler instruction
 - the type and the operands of the current assembler instruction
 - the type of the next assembler instruction

The type of the instructions are:
 - "0" for ADD(1-4), AND, CMP, CPY, EOR, MOV, ORR, ROR, SUB
 - "1" for LSL(2), LSR(2)
 - "2" for STR, STRB, STRH
 - "3" for LDR, LDRB, LDRH
 - "4" for MUL
 - "5" for the other instructions

```python
from elmo_online.engine import ELMOEngine
engine = ELMOEngine()
for i in range(0, 256):
  engine.add_point(
    (3, 4, 5), # Types of the previous, current and next instructions
    (0x0000, i), # Operands of the previous instructions
    (0x2BAC, i)  # Operands of the current instructions
  )
engine.run() # Compute the power consumption of all these points
power = engine.power # Numpy 1D array with an entry for each previous point
engine.reset_points() # Reset the engine to study other points
```

## Licences

[MIT](LICENCE.txt)

#ReVAMP : ReRAM based VLIW architecture for in-memory computing 



The arche framework supports behavioural simulation of the ReVAMP architecture[[PDF]](https://ieeexplore.ieee.org/document/7927095).  
For each simulation, a *configuration* file in *json* format has to be specified. We explain the configuration file with an example.

```
{
    "dim": {
        "m": 3,
        "n": 2
    },
    "filename": {
        "varin": "2_bit_xor.varin",
        "input": "2_bit_xor.inp",
        "ins_mem": "2_bit_xor.ins",
        "output": "2_bit_xor",
        "varout": "2_bit_xor.varout"
    },
    "simulation": {
        "gen_pwl": 1,
        "cycles": 0,
        "print_ins": 1,
        "verbose": 0
    },
    "voltage": {
        "0": -2.4,
        "1": 2.4,
        "delta": 5,
        "period": 50
    }
}
```

The individual fields are described below.

    + *dim* specifies DCM with *m* wordlines and *n* bitlines
    + *filename* specifies various files used for simulation
      + *varin* specfies the file with input specified as variables
      + *input* specifies the PIR contents
      + *ins_mem* defines the contents of the instruction memory
      + *output* specifies the prefix of the generated files
      + *varout* specifies the details of the output generated
    + *simulation* specifies the simulation parameters
      + *cycles* define the number of cycles for which simulation has to be performed. 0 indicates all instructions have to simulated.
      + *gen_pwl* specifies if pwl files for Cadence Simulation have to be generated. The *voltage* details must be specified, if this field has value 1.
    + *voltage* specifies the parameters used in the pwl files that can be imported directly in Cadence for simulating the crossbar.
      + 0 and 1 defines the voltage levels.
      + *delta* specifies the time in *ns* to switch between voltage levels
      + *period* specifies the clock time period in *ns* 


To start the tool, 
``` $ python3 arche.py 
Synthesis and technology mapping for emerging technologies
```

To execute the simulation, 
```
arche>revamp -f archesim/share_2inp/config_data.json 
Simulation started for: 0  cycles
Loading to PIR ['0', '1']
In reg: ['0', '1']
device: 1 wl: 1 bl 1
device: 0 wl: 1 bl 0
Cycle 1 : Apply 0 0 01 00 1 0 1 1
Crossbar state:
00
00
01
In reg: ['0', '1']
device: 1 wl: 1 bl 1
device: 0 wl: 1 bl 0
Cycle 2 : Apply 1 0 01 00 1 0 1 1
Crossbar state:
00
01
01
Loading to PIR ['1', '1']
In reg: ['1', '1']
device: 1 wl: 1 bl 1
device: 0 wl: 1 bl 1
Cycle 3 : Apply 2 0 01 00 1 0 1 1
Crossbar state:
00
01
01
DMR: [0, 0]
Cycle 4 : Read 2
Crossbar state:
00
01
01
In reg: [0, 0]
device: 1 wl: 0 bl 0
device: 0 wl: 0 bl 0
Cycle 5 : Apply 0 1 00 00 1 0 1 1
Crossbar state:
00
01
01
In reg: [0, 0]
device: 1 wl: 1 bl 0
device: 0 wl: 1 bl 0
Cycle 6 : Apply 1 1 01 00 1 0 1 1
Crossbar state:
00
11
01
DMR: [1, 1]
Cycle 7 : Read 1
Crossbar state:
00
11
01
In reg: [1, 1]
device: 1 wl: 1 bl 1
device: 0 wl: 1 bl 1
Cycle 8 : Apply 0 1 01 00 1 0 1 1
Crossbar state:
00
11
01
```

To quit the tool,

```arche>quit```
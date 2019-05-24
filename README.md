*Arche* is a Greek word with primary senses "beginning". The repository defines a framework for technology mapping of emerging technologies, with primary focus on ReRAMs. 


The repository has been tested with Python 3.6.7 on Ubuntu 14.04 and 18.04. 

### Start the tool
``` python3 arche.py ```

### View list of available commands
``` help ```

### Read a mapped verilog file
``` read test_map.v ```

### Single row technology mapping for MAGIC

The following command tries to find a solution for mapping the read verilog file with minimum number of devices (option `-md`) and with the minimum number of cycles (`-ms`).  There is a soft timelimit option in millisecs for the z3 solver using the `-t` flag. 
``` rowsat -md -ms -t 10000 ```

The output is shown in the terminal.
[cycle number] operation nodeid [Dev deviceid]


### Quit the tool
``` quit```

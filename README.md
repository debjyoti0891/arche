*Arche* is a Greek word with primary senses "beginning". The repository defines a framework for technology mapping of emerging technologies, with primary focus on ReRAMs. 


The repository has been tested with Python 3.6.7 on Ubuntu 14.04 and 18.04. 

### Start the tool
``` python3 arche.py ```

### View list of available commands
``` help ```

### Read a NOR/NOT mapped verilog file
``` read test_map.v ```

### Single row technology mapping for MAGIC

The following command tries to find a solution for mapping the read verilog file with minimum number of devices (option `-md`) and with the minimum number of cycles (`-ms`).  There is a soft timelimit option in millisecs for the z3 solver using the `-t` flag. 

``` rowsat -md -ms -t timelimit ```

The command can also be invoked to find solution to single row mapping of a file with a constraint on the number of steps (option `-s`) and the number of devices (option `-c`) avaiable for mapping. 

``` rowsat -s steps -c devices ```:w 

The output is shown in the terminal.

```[cycle number] operation nodeid [Dev deviceid]```


### Quit the tool
``` quit```

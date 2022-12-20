# Exercise 3: Reaction Kinetics Simulator
Program to simulate reactions over time for Part II Chemistry Programming Practical Exercise 3.

## Commands
* `time_simulate <mode> <json>` Simulates a reaction over time and generates a data output file in `/output_files`.
    * `<mode>`  Specifies mode to simulate reaction. The available modes are:
        * `fixed`   Runs reaction over a specified number of time intervals
        * `equillibrium`    Runs reaction until concentrations of all species remain within a specified equillibrium threshold, i.e., until the reaction reaches equillibrium
    * `<json>`  Specifies `.json` config file in `/reaction_configs` containing the parameters for the reaction.
    * Example: `time_simulate fixed oregonator`
    * Program will then prompt user to specify the output `.dat` file within the folder `/output_files` to write the data to
* `plot <json>` Plots the contents of a data file in `/output_files` as a graph.
    * `<json>`  Specifies the `.json` config file in `/plot_configs` containing the parameters for the plot.
    * Example: `plot oregonator_time`
    * Program will then prompt user to specify the input `.dat` file within the folder `/output_files` to read data from. 
* `protein_fold_data <json>`    Finds equillibrium concentrations of species in a protein folding reaction at varying concentrations of urea and generates a data output file in `/output_files`
    * `<json>`  Specifies the `.json` config file in `/reaction_configs` containing the reaction parameters and parameters about the range of urea concentration to generate data for.
    * Example: `protein_fold_data protein_folding`
* `help [<command>]`  Displays a list of available commands. If `<command>` is specified, returns syntax information for specific command
    * `<command>` (optional) If specified, shows detailed information for this command. 
    * Example: `help time_simulate`
* `quit` Exists the program. 

## Config files
### Reaction Config Files
* `parameters` Specifies various parameters for the reaction. 
    * `delta_t` Time interval by which each discrete step in the reaction simulation should progress. Lower values result in more accurate simulations but will take longer to simulate.
    * `equillibrium_threshold` Specifies value which the change between concentrations of all species between successive time steps must be less than in order for reaction to be considered at equillibrium. Lower values will give higher confidence that reaction has reached equillibrium but will take longer to reach this point. Note that if `delta_t` is changed `equillibrium_threshold` must be changed accordingly to account for the smaller time interval.
    * `max_cycles` Number of iterations to run simulation before stopping. If simulation mode is `fixed`, this specifies the number of cycles to run. If simulation mode is `equillibrium`, the simulation will stop when it reaches equillibrium or `max_cycles` is reached, whichever comes first.
    * `log_frequency` How often simulation should log progress to the console. E.g, a value of `1E3` logs to the console every 1000 iterations. Set to 0 for no logging. 
    * `sample_frequency` How often simulation should sample current data and record to the output file. E.g, a value of `1E3` means that every 1000th data point gets sampled. If set to 1, all data points are sampled. This allows for simulating a reaction over a small time scale for greater accuracy and over many iterations but without creating an output data file that is impractically large.
    * `urea_min` Lower bound of urea range to generate values for in the `protein_fold_data` command.
    * `urea_max` Upper bound of urea range to generate values for in the `protein_fold_data` command.
    * `urea_steps` Number of data points to generate values for in the `protein_fold_data` command.
* `species` Specifies each species involved in a reaction
    * `name` The name of the species, e.g. `"A"`
    * `init_conc` Initial concentration of the species, e.g. `1000`
* `processess` Specifies each process in a reaction
    * `name` The name of the step, e.g. `"R_1"`
    * `reactants` List of names of the species that are consumed in the step, e.g. `["A", "B"]`
    * `products` List of names of the species that are produced in the step, e.g. `["C"]`
    * `rate` The rate constant for the step, e.g. `1E-4`
    * `denaturant_constant` Specifies constant used for calculating the change in rate in the presence of a denaturant such as urea, e.g. `-1.68`

### Plot Config Files
* `xvar` Name of the independent variable for the plot
* `yvars` List of names of the variables that should be plotted against `xvar`
* `xlabel` Label for the x-axis
* `ylabel` Label for the y-axis
* `yscale` Specifies what scaling should be used for the y-axis, e.g. `linear` for a linear scale, `log` for a logarithmic scale
* `scatter` If set to `true` displays individual data points as well as the curve on the graph. 
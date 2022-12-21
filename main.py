from reaction import *
import numpy as np
import matplotlib.pyplot as plt
import json
import os
import time

class Timer():
    #Simple object to handle timing of program run times    
    def start(self):
        self.tlast = time.time()
    
    def stop(self):
        t = time.time() - self.tlast
        print("Time: %.0f s" % t)
        return t

#UI Functions

def welcome_message():
    print("----------------")
    print("Reaction Kinetics Simulator")

def commands():
    print("----------------")
    print("Available commands:\n")
    for key in COMMAND_SYNTAX.keys():
        print("{0: <20}".format(key) + COMMAND_SYNTAX[key]["description"])

def load_command_syntax():
    #Gets information about commands from json file
    global COMMAND_SYNTAX
    with open("commands.json","r") as f:
        COMMAND_SYNTAX = json.load(f)

def correct_syntax(com):
    #Prints syntax usage for a command
    print("Syntax for %s: \t %s" % (com, COMMAND_SYNTAX[com]["syntax"]))

def command_input():
    #Parse user command
    valid = False
    while not valid:
        inp = input().lower().strip().split(" ")
        command = inp[0]
        args = inp[1:]
        if command == "time_simulate":
            time_simulate(args)
            valid = True
        elif command == "plot":
            plot(args)
            valid = True
        elif command == "protein_fold_data":
            generate_protein_fold_data(args)
            valid = True
        elif command == "help":
            if len(args) == 0:
                commands()
            else:
                try:
                    info  = COMMAND_SYNTAX[args[0]]
                    for key in info.keys():
                        print("{0: <16}".format(key) + info[key])
                except:
                    print("Unknown command")
        elif command == "quit":
            exit()
        else:
            print("Invalid command")

#Functions to run user commands

def time_simulate(args):
    """
    Simulates reaction over time and generates output data file
    """
    #Parse command arguments and stop function if syntax invalid
    try:
        file = args[1].replace(".json","") + ".json"
        mode = args[0].strip().lower()
    except:
        print("Invalid syntax")
        correct_syntax("time_simulate")
        return None

    if mode not in ["fixed","equillibrium"]:
        print("Invalid mode")
        return None

    #Get parameters for reaction
    t = Timer()
    try:
        rxn, parameters = reaction_from_json(file)
    except:
        print("File not found")
        return None
    dir = specify_output_file()
    
    delta_t = float(parameters["delta_t"])
    max_cycles = int(parameters["max_cycles"])
    sample_freq = int(parameters["sample_frequency"])
    equillibrium_threshold = float(parameters["equillibrium_threshold"])
    log = int(parameters["log_frequency"])
    

    #Run appropriate simulation
    t.start()
    if mode == "fixed":
        data = simulate_fixed(
                            rxn, 
                            delta_t, 
                            max_cycles, 
                            log=log, 
                            sample_freq=sample_freq
                    )

    if mode == "equillibrium":
        data = simulate_to_equillibrium(
                            rxn,
                            delta_t,
                            equillibrium_threshold,
                            max_cycles=max_cycles,
                            log=log,
                            sample_freq=sample_freq
        )

    parameters["Run Time"] = t.stop()
    
    time_evolution_output_file(data, parameters,dir)

def plot(args):
    """
    Plots data from a data file
    """
    #Parse command arguments and stop function if syntax invalid
    try:
        file = args[0].replace(".json","") + ".json"
    except:
        print("Invalid syntax")
        correct_syntax("plot")
        return None
    
    #Get parameters
    try:
        #Load json data
        with open("plot_configs\\"+file,"r") as f:
            config = json.load(f)
    except:
        print("File not found")
        return None
    
    #Load data
    data = get_data_from_file(specify_input_file())

    #Show plot
    plot_data(
        data, 
        config["xvar"], 
        config["xlabel"], 
        config["ylabel"], 
        yscale=config["yscale"], 
        vars=config["yvars"],
        scatter=config["scatter"]
    )

def generate_protein_fold_data(args):
    """
    Simulates protein folding reaction over a range of urea values and 
    generates output data file.
    """
    #Parse command arguments and stop function if syntax invalid
    try:
        file = args[0].replace(".json","") + ".json"
    except:
        print("Invalid syntax")
        correct_syntax("protein_fold_data")
        return None

    #Get parameters
    try:
        with open("reaction_configs\\"+file,"r") as f:
            jsondata = json.load(f)
    except:
        print("File not found")
        return None

    u_min = jsondata["parameters"]["urea_min"]
    u_max = jsondata["parameters"]["urea_max"]
    u_steps = jsondata["parameters"]["urea_steps"]

    #Generate header for output file
    info  = ""
    info += "Parameters: \n"
    for key in jsondata["parameters"].keys():
        info += "%s : %f \n" % (key, jsondata["parameters"][key])
    info += "\nInitial concentrations: \n"
    for s in jsondata["species"]:
        info += "%s : %f \n" % (s["name"], s["init_conc"])

    dir = specify_output_file()

    #Generate the data
    data = values_over_urea_range(u_min, u_max, u_steps, file)
    write_to_file(data, dir, info)

#Reaction simulation functions

def simulate_fixed(reaction, delta_t, steps, log=0, sample_freq=1):
    """
    Simulates reaction over a specified number of steps with time interval 
    delta_t. Returns a dictionary of arrays, one for time and one for the
    concentration of each species at each point in time.

    If log is specified, logs progress in console every log interations.

    If sample_freq is specified only adds data every sample_freq iterations to
    the array. This allows simulating a reaction with a finer timescale than 
    the output data, which would otherwise result in very large output files.
    """
    #Set up arrays to store the data and store within dictionary 'data'
    data = {}
    data["t"] = []
    keys = []
    for key in reaction.get_species_keys():
        keys.append(key)
        data[key] = []
    
    #Simulation loop - store data at each point in time and then update
    for i in range(steps):
        
        #Tick reaction
        reaction.tick(delta_t)

        #Only record data every sample_freq samples
        if i % sample_freq ==0:
            data["t"].append(delta_t * i)
            c = reaction.get_concs()
            for key in keys:
                data[key].append(c[key])
        
        #Log progress
        if log != 0:
            if i % log == 0:
                p = '{:.0%}'.format(i / steps)

                print("Completed %i / %i iterations (%s)" % (i, steps, p))

    return data

def simulate_to_equillibrium(
    reaction, 
    delta_t, 
    gradient, 
    max_cycles=0,
    log=0,
    sample_freq=1
):
    """
    Simulates reaction with time interval delta_t until the difference in
    concentration of all species between successive steps is less than the 
    specified threshold - this is taken to mean the system is at equillibrium.

    By specifying max_cycles the simulation will stop once this number of 
    cycles is reached, regardless of whether equillibrium has been reached or
    not. 

    If log is specified, logs progress in console every log interations.
    
    If sample_freq is specified only adds data every sample_freq iterations to
    the array. This allows simulating a reaction with a finer timescale than 
    the output data, which would otherwise result in very large output files.
    """
    #Set up dictionary to store data. We cannot predetermine the size of the
    #arrays as we don't know how many steps the simulation will run for
    data = {"t":[]}
    keys = []
    for key in reaction.get_species_keys():
        keys.append(key)
        data[key] = []

    equillibrium_reached = False
    i = 0
    c = reaction.get_concs()
    threshold = gradient * delta_t

    #Run the simulation indefinitely until 'equillibrium' is reached
    while not equillibrium_reached:
        c_prev = c
    
        i += 1  
        reaction.tick(delta_t)
        c = reaction.get_concs()
        number_out_of_range = 0

        #Check all species are within specified 'equillibrium' threshold
        for key in keys:
            
            if c[key] > c_prev[key] + threshold \
            or c[key] < c_prev[key] - threshold:
                number_out_of_range += 1
        
        if number_out_of_range == 0:
            print("Equillibrium reached after %i cycles" % i)
            equillibrium_reached = True

        if i > max_cycles and max_cycles !=0:
            print("Reached maximum number of cycles (%i) before reaching\
            equillibrium" %max_cycles)
            equillibrium_reached = True
        
        #Only add data to arrays every sample_freq steps
        if i % sample_freq ==0:
            data["t"].append(delta_t * i)
            for key in keys:
                data[key].append(c[key])

        #Log progress every log steps
        if log != 0:
            if i % log == 0:
                print("Running iteration %i" %i)
        
    
    return data

#Specific functions for urea concentration plot

def denaturant_rate_multiply(rate, conc, constant):
    """
    Calculates modified rate constant at a given concentration of denaturant
    and a specified constant for the step.
    """
    k = rate * np.exp(conc * constant)
    return k

def get_equillibrium_values(data, keys):
    """
    Returns the final values from reaction data - these correspond to the 
    equillibrium values if reaction was run to equillibrium
    """
    values = {}
    for key in keys:
        size = len(data[key])
        values[key] = data[key][size-1]
    
    return values

def values_over_urea_range(conc_min, conc_max, count, file):
    """
    Simulates reaction over a range of urea values and generates output data
    """
    #Setup output dictionary
    urea_range = np.linspace(conc_min, conc_max, count)
    output = {}
    output["urea"] = urea_range
    arrays_initialised = False

    #Run reaction at each urea value
    for i in range(len(urea_range)):
        u = urea_range[i]
        print("Simulating reaction at urea concentration %.2f..." % u)

        #Setup reaction
        reaction, parameters = reaction_from_json(
            file,
            denaturant_conc=u
        )

        #Get parameters
        delta_t = parameters["delta_t"]
        equillibrium_threshold = parameters["equillibrium_threshold"]
        max_cycles = parameters["max_cycles"]

        #Simulate reaction
        data = simulate_to_equillibrium(reaction,
                                        delta_t, 
                                        equillibrium_threshold, 
                                        max_cycles=max_cycles
                                        )
        
        #Get equillibrium values
        keys = reaction.get_species_keys()
        eq_values = get_equillibrium_values(data, keys)

        #Setup arrays on first loop
        if not arrays_initialised:
            for key in keys:
                output[key] = np.zeros(len(urea_range))
            arrays_initialised = True
        
        #Update output arrays with equillibrium values
        for key in keys:
            output[key][i] = eq_values[key]

    return output

#Various file handling functions

def specify_output_file():
    #Handles user specifying data output file
    valid_file = False
    while not valid_file:
        try:
            print("Please enter name of output file: ")
            name = input().strip().replace(".dat","")
            dir = "output_files\\%s.dat" % name
            f = open(dir, "x")
            f.close()
            valid_file = True
        except FileExistsError:
            print("File already exists")
        except:
            print("Invalid file name")
    return dir 

def specify_input_file():
    #Handles user specifying input data file
    valid_file = False
    while not valid_file:
        try:
            print("Please enter name of input file: ")
            name = input().strip().replace(".dat","")
            dir = "output_files\\%s.dat" % name
            f = open(dir)
            f.close()
            valid_file = True
        except FileNotFoundError:
            print("File not found.")
        except:
            print("Unable to open file.")
    return dir

def write_to_file(data, dir, info):
    #Generates output data file
    with open(dir, "w") as f:
        
        #Add information that won't be read as data
        f.write(info + "\n")

        #Signify start of actual data
        f.write("DATA START\n")
        keys = data.keys()

        #Generate column headers 
        header = ""
        size = 0
        for key in keys:
            header += "{0: <24}|".format(key)
            if size == 0:
                size = len(data[key])
        f.write(header + "\n")

        #Add data
        for i in range(size):
            line = ""
            for key in keys:
                s = str("%.16e" % data[key][i])
                line += "{0: <24}|".format(s)    
            f.write(line + "\n")

def get_data_from_file(dir):
    #Gets data from file generated by write_to_file()
    with open(dir, "r") as f:
        data_mode = False
        data = {}
        for i, line in enumerate(f):
            #Only start reading data once in data mode
            if data_mode:
                if i == start_point + 1:
                    #Read column headers
                    keys = line.strip().split("|")
                    for j, key in enumerate(keys[:len(keys)-1]):
                        keys[j] = key.strip()
                        data[keys[j]] = np.array([])
                else:
                    #Read data values
                    values = line.split("|")
                    for j, value in enumerate(values[:len(values)-1]):
                        key = keys[j]
                        value = float(value.strip())
                        data[key] = np.append(data[key], value)
            #Enter data mode once line 'DATA START' is reached
            if line[:10] == "DATA START":
                start_point = i
                data_mode = True  
    return data

def reaction_from_json(json_file, denaturant_conc=0):
    """
    Creates a Reaction object using data from the specified json config
    file. 

    Returns a tuple of the Reaction object and a dictionary object containing
    the parameters from the json file. 

    If denaturant_conc is not 0 rates in the reaction for the appropriate steps
    are modified according to the concentration of denaturant.
    """

    #Load json data
    with open("reaction_configs\\"+json_file,"r") as f:
        data = json.load(f)
    
    #Create Reaction object and add Species and Process objects 
    reaction = Reaction()
    for i in data["species"]:
        name = i["name"]
        init_conc = i["init_conc"]
        reaction.add_species(name, init_conc)

    for entry in data["processes"]:
        reactants = entry["reactants"]
        products = entry["products"]
        rate = entry["rate"]
        if denaturant_conc != 0:
            denaturant_constant = entry["denaturant_constant"]
            rate = denaturant_rate_multiply(rate, 
                                            denaturant_conc, 
                                            denaturant_constant)
        reaction.add_process(reactants, products, rate)

    parameters = data["parameters"]
    output = (reaction, parameters)
    return output

def time_evolution_output_file(data, parameters, dir):
    #Makes output file for data of a reaction over time
    info  = ""
    info += "Parameters: \n"
    for key in parameters.keys():
        info += "%s : %f \n" % (key, parameters[key])
    
    write_to_file(data, dir, info)

#Other functions

def scale_data(data, independent_var):
    #Scales down all data except independent_var to sum to 1 at 0
    keys = data.keys()
    scale = 0
    for key in keys:
        if key != independent_var:
            scale += data[key][0]

    for key in keys:
        if key != independent_var:
            data[key] = data[key] / scale
    
    return data

def plot_data(
                data, 
                variable,
                xlabel, 
                ylabel, 
                scatter=False, 
                curve=True,
                yscale="linear",
                vars=[]):
    """
    Shows plot of data with various parameters that can be specified.
    """
    if vars == []:
        vars = data.keys()
    for key in vars:
        if key != variable:
            if curve:
                plt.plot(data[variable], data[key], linewidth=1, label=key)
            if scatter:
                plt.scatter(data[variable], 
                            data[key],
                            marker="x", 
                            label=key, 
                            s=10)
    plt.yscale(yscale)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.show()

####################
#   Main Program   #
####################

#Startup
load_command_syntax()
#Main Program Loop
while True:
    welcome_message()
    commands()

    command_input() #Set default=True for testing

    input("Press enter to continue...")
exit()


class Reaction:
    """
    Class to hold all information for a specified reaction.

    Variables:
        species_list:   dict    Stores each species in the reaction as an
                                entry in a dictionary.
        processes:      array   Stores each process in the reaction as a
                                dictionary object in an array

    Methods:
        add_species(self, name, species)    Adds a species to list
        add_process(self, process)          Adds a process to list
        tick(self, delta_t)                 Proceeds reaction by time interval
        get_species_keys(self)              Returns list of keys for each
                                            species
        get_concs(self)                     Returns concentrations of each
                                            species
        log(self)                           Prints out information about           
                                            Reaction object to console
    """

    def __init__(self):
        """
        Initialise lists of species and processes but don't add any to start
        """

        self.species_list = {}
        self.processes = []
    
    def add_species(self, name, init_conc):
        """ Adds entry to the species list with key 'name' """
        self.species_list[name] = {
            "conc":init_conc,
            "delta_conc":0.0
        }
    
    def add_process(self, reactants, products, rate):
        """Adds a Proces object to the list of processes"""
        process = {
            "reactants":reactants,
            "products":products,
            "rate":rate
        }
        self.processes.append(process)

    def tick(self, delta_t):
        """
        Updates all species according to each process over time interval 
        delta_t
        """

        #Iterate over each process in the list and calculate the necessary
        #change in concentration of each species for the given time interval
        for process in self.processes:
            reactants = process["reactants"]
            products = process["products"]
            k = process["rate"]

            #Calculate change in concentration for this process step
            change = k * delta_t
            for r in reactants:
                change =  change * self.species_list[r]["conc"]
            
            #Decrease concentration of each reactant by this amount
            for r in reactants:
                self.species_list[r]["delta_conc"] += -change
                
            
            #Increase concentration of each product by this amount
            for p in products:
                self.species_list[p]["delta_conc"] += change
        
        for key in self.species_list.keys():
            self.species_list[key]["conc"] += \
                self.species_list[key]["delta_conc"]
            self.species_list[key]["delta_conc"] = 0.0 

    def get_species_keys(self):
        """
        Gets a list of all keys in the dictionary of Species objects
        """
        return self.species_list.keys()

    def get_concs(self):
        """
        Returns concentrations of each species as a dictionary
        """
        d = {}
        for key in self.species_list.keys():
            d[key] = self.species_list[key]["conc"]
        return d
            
    def log(self):
        for key in self.get_species_keys():
            conc = self.species_list[key]["conc"]
            print(key, conc)

        for process in self.processes:
            reactants = process["reactants"]
            products = process["products"]
            rate = process["rate"]
            print(reactants, products, rate)
    



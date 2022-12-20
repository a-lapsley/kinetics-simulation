from process import *

class Reaction:
    """
    Class to hold all information for a specified reaction.

    Variables:
        species_list:   dict    Stores each species in the reaction as a
                                Species object in a dictionary.
        processes:      array   Stores each process in the reaction as a
                                Process object in an array

    Methods:
        add_species(self, name, species)    Adds a Species object to list
        add_process(self, process)          Adds a Process object to list
        tick(self, delta_t)                 Proceeds reaction by time interval
        update_all_species(self)            Updates actual concentration of 
                                            each species
        reset_all(self)                     Resets all concentrations to
                                            initial values
        get_species_keys(self)              Returns list of keys for each
                                            species
        get_concs(self)                     Returns concentrations of each
                                            species          
    """

    def __init__(self):
        """
        Initialise lists of species and processes but don't add any to start
        """

        self.species_list = {}
        self.processes = []
    
    def add_species(self, species):
        """ Adds a Species object to the species list with key 'name' """
        name = species.get_name()
        self.species_list[name] = species
    
    def add_process(self, process):
        """Adds a Proces object to the list of processes"""
        self.processes.append(process)

    def tick(self, delta_t):
        """
        Updates all species according to each process over time interval 
        delta_t
        """

        #Iterate over each process in the list and calculate the necessary
        #change in concentration of each species for the given time interval
        for process in self.processes:
            reactants = process.get_reactants()
            products = process.get_products()
            k = process.get_rate()

            #Calculate change in concentration for this process step
            change = k * delta_t
            for r in reactants:
                change =  change * self.species_list[r].get_conc()
            
            #Decrease concentration of each reactant by this amount
            for r in reactants:
                self.species_list[r].add_to_delta_conc(-change)
            
            #Increase concentration of each product by this amount
            for p in products:
                self.species_list[p].add_to_delta_conc(change)
        
        self.update_all_species()
        
    def update_all_species(self):
        """
        For each species updates the actual concentration of the species
        according to the total change in concentration from one step of each
        process
        """
        for key in self.species_list.keys():
            self.species_list[key].update_conc()

    def reset_all(self):
        """
        Reset concentration of all species to the initial value
        """
        for key in self.species_list.keys():
            self.species_list[key].reset()

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
            d[key] = self.species_list[key].get_conc()
        return d
            
    def log(self):
        for key in self.get_species_keys():
            species = self.species_list[key]
            name = species.get_name()
            conc = species.get_conc()
            print(name, conc)

        for process in self.processes:
            reactants = process.get_reactants()
            products = process.get_products()
            rate = process.get_rate()
            print(reactants, products, rate)
    



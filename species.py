class Species:
    """
    Stores information about a species in a reaction.
    Variables:
        name        string  Name of the species
        conc_init   float   Initial concentration of species
        conc        float   Current concentration of species
        delta_conc  float   Amount by which concentration should change after
                            a time step

    Methods:
        get_name(self)                  Returns name of the species
        get_conc(self)                  Returns current concentration
        add_to_delta_conc(self, amount) Changes delta_conc by specified amount
        update_conc(self)               Updates conc by value of delta_conc
        reset(self)                     Reverts value of conc to initial value
    """


    def __init__(self, name, conc):
        self.name = name
        self.conc_init = conc
        self.conc = self.conc_init
        self.delta_conc = 0.0
    
    def get_name(self):
        return self.name
    
    def get_conc(self):
        """Returns current concentration of species"""
        return self.conc
    
    def update_conc(self):
        """
        Updates actual concentration according to value of delta_conc and then
        resets value of delta_conc to 0 for next iteration.
        """
        self.conc = self.conc + self.delta_conc
        self.delta_conc = 0.0
    
    def add_to_delta_conc(self, amount):
        """Changes delta_conc by specified amount"""
        self.delta_conc += amount
    
    def reset(self):
        """Resets concentration to initial value"""
        self.conc = self.conc_init
    


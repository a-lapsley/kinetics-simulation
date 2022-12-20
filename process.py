class Process:
    """
    Stores information about a specific step in a reaction.
    
    Variables:
        reactants:  tuple   List of keys for the reactants in the process
        produts:    tuple   List of keys for the products in the process
        rate:       float   Rate constant for the process
    
    Methods:
        get_reactants(self) Returns list of keys for the reactants
        get_products(self)  Returns list of keys for the products
        get_rate(self)      Returns rate of the process
    """
    def __init__(self, reactants, products, rate):
        self.reactants = reactants
        self.products = products
        self.rate = rate

    def get_reactants(self):
        """Returns list of keys for the reactants"""
        return self.reactants
    
    def get_products(self):
        """Returns list of keys for the products"""
        return self.products
    
    def get_rate(self):
        """Returns rate of the process"""
        return self.rate
    
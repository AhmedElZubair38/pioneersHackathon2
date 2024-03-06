
# class Blend:

#     def __init__(self, blend_code, description, required_rm):
#         self.blend_code = blend_code
#         self.description = description
#         self.required_rm = required_rm  # This will be a dictionary with RM codes as keys and required quantities as values
#         self.stock_levels = {}  # This will hold stock levels at different locations
        
#     def add_stock(self, location, quantity):
#         # This method will add stock to a location
#         pass
        
#     def reduce_stock(self, location, quantity):
#         # This method will reduce stock from a location
#         pass

# Blend class represents the different tea blends.
class Blend:
    def __init__(self, blend_code, description):
        self.blend_code = blend_code
        self.description = description
        self.stock_levels = {}  # Stores stock levels at different locations

    def add_stock(self, location, quantity):
        if location in self.stock_levels:
            self.stock_levels[location] += quantity
        else:
            self.stock_levels[location] = quantity

    def reduce_stock(self, location, quantity):
        if location in self.stock_levels and self.stock_levels[location] >= quantity:
            self.stock_levels[location] -= quantity
            return True
        else:
            return False  # Not enough stock to reduce

    def __repr__(self):
        return f"Blend({self.blend_code}, Stock Levels: {self.stock_levels})"
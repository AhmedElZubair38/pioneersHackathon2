
# class Silo:

#     def __init__(self, name, capacity, transfer_type):
#         self.name = name
#         self.capacity = capacity
#         self.current_stock = {}  # This will be a dictionary with blend codes as keys and quantities as values
#         self.transfer_type = transfer_type
        
#     def transfer_to(self, destination, blend_code, quantity):
#         # This method will handle the logic for transferring stock to a destination
#         pass

class Silo:

    def __init__(self, name, capacity, transfer_type):
        self.name = name
        self.capacity = int(capacity.replace(',', ''))  # Remove commas and convert to integer
        self.current_stock = {}  # To keep track of the blend and its quantity
        self.transfer_type = transfer_type

    def transfer_to(self, destination, blend_code, quantity):
        # Logic for transferring tea blend to a production line or other location
        if blend_code in self.current_stock and self.current_stock[blend_code] >= quantity:
            self.current_stock[blend_code] -= quantity
            # Assume destination is a ProductionLine object with a receive_blend method
            destination.receive_blend(blend_code, quantity)
            return True
        else:
            return False  # Not enough stock to transfer

    def add_stock(self, blend_code, quantity):
        if blend_code in self.current_stock:
            self.current_stock[blend_code] += quantity
        else:
            self.current_stock[blend_code] = quantity

    def __repr__(self):
        return f"Silo({self.name}, Capacity: {self.capacity}, Stock: {self.current_stock})"
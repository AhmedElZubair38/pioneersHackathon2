
# class ProductionLine:

#     def __init__(self, name, consumption_rate, efficiency):
#         self.name = name
#         self.consumption_rate = consumption_rate
#         self.efficiency = efficiency
#         self.current_blend = None  # This will hold the blend currently being processed
        
#     def produce(self, blend_code, time):
#         # This method will simulate the production process
#         pass


# ProductionLine class represents each production line where a specific blend is packed.
class ProductionLine:
    def __init__(self, name, consumption_rate, efficiency):
        self.name = name
        self.consumption_rate = int(consumption_rate.replace(',', ''))  # Remove commas and convert to integer
        self.efficiency = int(efficiency.replace('%', '')) / 100  # Convert percentage to decimal
        self.current_blend = None
        self.produced_quantity = 0

    def produce(self, time):
        if self.current_blend:
            # Calculate the quantity produced based on time, rate and efficiency
            produced = (self.consumption_rate * self.efficiency) * time
            self.produced_quantity += produced
            return produced
        else:
            return 0

    def receive_blend(self, blend_code, quantity):
        self.current_blend = blend_code
        # We assume the quantity received is ready to be processed and doesn't require storage

    def __repr__(self):
        return (f"ProductionLine({self.name}, Rate: {self.consumption_rate}, "
                f"Efficiency: {self.efficiency}, Current Blend: {self.current_blend}, Produced: {self.produced_quantity})")
import random
from deap import base, creator, tools, algorithms

class FactoryScheduler:
    def _init_(self, schedule_data, locations_info):
        self.schedule_data = schedule_data
        self.locations_info = locations_info
        self.toolbox = self._initialize_ga()

    def _initialize_ga(self):
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)

        toolbox = base.Toolbox()
        toolbox.register("attr_int", random.randint, 0, len(self.schedule_data) - 1)
        toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_int, n=len(self.schedule_data))
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("evaluate", self.evaluate_individual)
        toolbox.register("mate", tools.cxTwoPoint)
        toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)
        toolbox.register("select", tools.selTournament, tournsize=3)

        return toolbox

    def decode_individual_to_schedule(self, individual):
        return [self.schedule_data[index] for index in individual]

    def is_valid_schedule(decoded_schedule, locations_info, lines_info):
        lines_per_location = dict(list)
        total_time_per_location = dict(int)

        for task in decoded_schedule:
            location = task["Location"]
            line_name = task["Line Name"]
            max_capacity = locations_info.get(location, {}).get("Max Capacity", 0)
            working_mode = locations_info.get(location, {}).get("Working Mode", "continuous")
            time_to_finish = lines_info.get(line_name, 0)

            # Constraint 1: One Silo or Transfer Station can be connected to a maximum of 2 lines
            if location not in ["Silo A", "Silo B"]:
                lines_per_location[location].append(line_name)
                if len(lines_per_location[location]) > 2:
                    return False

            # Constraint 2: One line can be connected to one Silo or Transfer Station
            if location in lines_per_location.values():
                return False

            # Constraint 3: Each location can hold one blend at a time
            if location in total_time_per_location:
                return False

            # Constraint 4: Each production line can only pack one type of blend at any given time
            if location not in ["Silo A", "Silo B"] and line_name in total_time_per_location:
                return False

            # Check location capacity constraints
            if max_capacity > 0 and task["Quantity(kg)"] > max_capacity:
                return False

            # Update the total time spent on each location
            total_time_per_location[location] += time_to_finish

        # Additional constraints based on batch transfers
        for task in decoded_schedule:
            if task["Location"] == "Warehouse" and task["Transfer Mode"] == "Batch":
                batch_size = locations_info.get("Warehouse", {}).get("Max Capacity", 0)
                transfer_time = locations_info.get("Warehouse", {}).get("Transfer Time", 0)
                if task["Quantity(kg)"] % batch_size != 0:
                    return False
                # Add specific conditions based on batch transfers, if needed

        return True


    def evaluate_individual(self, individual):
        decoded_schedule = self.decode_individual_to_schedule(individual)

        # Check if the schedule is valid
        if not self.is_valid_schedule(decoded_schedule):
            return (float('-inf'),)

        # Placeholder calculations for optimization objectives
        waiting_time = self.calculate_waiting_time(decoded_schedule)
        discrepancy_penalty = self.calculate_discrepancy_penalty(decoded_schedule)
        

        # Combine objectives into a single fitness value
        fitness = -(waiting_time + discrepancy_penalty)

        return (fitness,)

    def calculate_waiting_time(self, decoded_schedule):
        total_waiting_time = 0

        # Dictionary to store the end times of production lines
        end_times = {}

        for task in decoded_schedule:
            production_line = task['Production Line']
            start_time = task['Start Time']
            end_time = task['End Time']

            # Update the end time for the production line
            end_times[production_line] = end_time

            # Calculate waiting time for the current task
            waiting_time = max(0, start_time - end_times.get(production_line, 0))
            total_waiting_time += waiting_time

        return total_waiting_time
    



    def calculate_discrepancy_penalty(self, decoded_schedule):
        total_discrepancy_penalty = 0

        for task in decoded_schedule:
            required_quantity = task['Required Quantity']
            produced_quantity = task['Produced Quantity']
            discrepancy_penalty_factor = task.get('Discrepancy Penalty Factor', 1.0)

            # Calculate the absolute difference between required and produced quantities
            discrepancy = abs(required_quantity - produced_quantity)

            # Penalize the discrepancy using a penalty factor
            discrepancy_penalty = discrepancy * discrepancy_penalty_factor

            # Add the discrepancy penalty to the total
            total_discrepancy_penalty += discrepancy_penalty

        return total_discrepancy_penalty


    def optimize_schedule_with_ga(self, population_size=300, num_generations=40, crossover_probability=0.5, mutation_probability=0.2):
        pop = self.toolbox.population(n=population_size)

        stats = tools.Statistics(key=lambda ind: ind.fitness.values)
        stats.register("avg", numpy.mean)
        stats.register("std", numpy.std)
        stats.register("min", numpy.min)
        stats.register("max", numpy.max)

        pop, logbook = algorithms.eaSimple(pop, self.toolbox, crossover_probability, mutation_probability, num_generations, stats=stats, verbose=True)

        best_ind = tools.selBest(pop, 1)[0]
        print("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))

        schedule = self.decode_individual_to_schedule(best_ind)
        # Your specific logic to process and print the final schedule
        # Example: Print decoded schedule

if _name_ == "_main_":
    # Example data, replace with your actual schedule_data and locations_info
    schedule_data = [...]  # Your actual schedule data
    locations_info = {...}  # Your actual locations information

    factory_scheduler = FactoryScheduler(schedule_data, locations_info)
    factory_scheduler.optimize_schedule_with_ga()
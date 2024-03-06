
# # class Scheduler:

# #     def __init__(self, production_schedule, rm_availability, blend_stock, consumption_rates, transfer_times):
# #         self.production_schedule = production_schedule
# #         self.rm_availability = rm_availability
# #         self.blend_stock = blend_stock
# #         self.consumption_rates = consumption_rates
# #         self.transfer_times = transfer_times
        
# #     def optimize_schedule(self):
# #         # This method will create the optimized schedule
# #         pass

# from TransferTimeMatrix import TransferTimeMatrix
# from ProductionLine import ProductionLine
# from Blend import Blend
# from Silo import Silo

# import pandas as pd
# from deap import base, creator, tools, algorithms
# import random


# # Example CSV loading
# production_schedule_df = pd.read_csv('path/to/your/production.csv')
# rm_availability_df = pd.read_csv('path/to/your/RM.csv')
# blend_stock_availability_df = pd.read_csv('path/to/your/blendstock.csv')
# consumption_rates_efficiency_df = pd.read_csv('path/to/your/consumption_rates_and_efficiency.csv')
# updated_parameters_df = pd.read_csv('path/to/your/parameters.csv')  # If you have parameters CSV


# # Initializing blends from the blendstock data.
# class Scheduler:
#     def __init__(self, production_schedule_df, rm_availability_df, blend_stock_availability_df, consumption_rates_efficiency_df, transfer_time_matrix):
#         self.production_schedule_df = production_schedule_df
#         self.rm_availability_df = rm_availability_df
#         self.blend_stock_availability_df = blend_stock_availability_df
#         self.consumption_rates_efficiency_df = consumption_rates_efficiency_df
#         self.transfer_time_matrix = transfer_time_matrix  # Instance of TransferTimeMatrix

#         # Initializing entities
#         self.silos = {}
#         self.production_lines = {}
#         self.blends = {}

#         self._initialize_entities()

#     def _initialize_entities(self):
#         # Initialize silos from parameters data
#         for index, row in updated_parameters_df.iterrows():
#             self.silos[row['Name']] = Silo(row['Name'], row['Maximum Capacity (kg)'], row['Transfer Type'])

#         # Initialize production lines from consumption data
#         for index, row in consumption_rates_efficiency_df.iterrows():
#             self.production_lines[row['Name']] = ProductionLine(row['Name'], row['Ideal Consumption Rate (kg/h)'], row['Efficiency (%)'])

#         # Initialize blends from blendstock data
#         for index, row in blend_stock_availability_df.iterrows():
#             blend_code = row['Blend Code']
#             if blend_code not in self.blends:
#                 self.blends[blend_code] = Blend(blend_code, row['Blend Description'])
#             # Add the stock information to the blend
#             self.blends[blend_code].add_stock(row['Location'], row['Quantity (kg)'])

#         # Add raw material availability to silos from RM data
#         for index, row in rm_availability_df.iterrows():
#             silo_name = row['Location']
#             blend_code = row['Blend Code']
#             quantity = row['Quantity (kg)']
#             if silo_name in self.silos:
#                 self.silos[silo_name].add_stock(blend_code, quantity)

#     def optimize_schedule(self):
#         # Heuristic Approach:
#         # 1. Sort production tasks based on priority, e.g., due date, quantity.
#         sorted_tasks = self.sort_tasks(self.production_schedule_df)
        
#         # 2. For each task, select the best line and time slot minimizing the idle time and meeting the constraints.
#         for task in sorted_tasks:
#             best_line, start_time = self.find_best_line_and_time(task)
            
#             # 3. Schedule the task on the selected line and time.
#             if best_line:
#                 self.schedule_task(best_line, task, start_time)
#             else:
#                 print(f"Cannot schedule task {task['SKU Code']} due to constraints.")
        
#         # - find_best_line_and_time: Identifies the optimal production line and start time for a task.
#         # - schedule_task: Assigns the task to the schedule, updating resources and timings.

#     # - sort_tasks: Orders tasks based on certain criteria.
#     def sort_tasks(self, tasks_df):
#         # Example: Sort by earliest due date and then by quantity, descending.
#         return tasks_df.sort_values(by=['Due Date', 'Quantity (kg)'], ascending=[True, False])

#     def find_best_line_and_time(self, task):
#         best_line = None
#         best_start_time = float('inf')
#         best_fit_metric = float('inf')

#         for line_name, line in self.production_lines.items():
#             available, start_time = self.check_line_availability(line, task)
#             if available:
#                 fit_metric = self.calculate_fit_metric(line, task, start_time)
#                 if fit_metric < best_fit_metric:
#                     best_line = line
#                     best_start_time = start_time
#                     best_fit_metric = fit_metric

#         return best_line, best_start_time

#     def check_line_availability(self, line, task):
#         # Placeholder logic for checking line availability.
#         # In a real scenario, this would involve looking at the line's schedule and finding the next available time slot.
#         # For simplicity, let's assume every line is initially available at time 0.
#         return True, 0  # Indicating line is available from time 0.

#     def calculate_fit_metric(self, line, task, start_time):
#         # A simple fit metric might consider the efficiency of the line for the specific task and the expected idle time.
#         # Lower values are better. Let's give efficiency a higher weight.
#         efficiency = line.efficiency
#         idle_time = start_time - task['Last Finish Time']  # Hypothetical 'Last Finish Time' for a task's line.
#         fit_metric = idle_time - efficiency  # Simplified metric for demonstration.
#         return fit_metric

#     def schedule_task(self, line, task, start_time):
#         # Here, we would update the line's schedule to include the new task.
#         # Additionally, update the stock levels and any other necessary information.
#         # For simplicity, let's represent the line's schedule as a list of tasks.
#         line.schedule.append({'task': task, 'start_time': start_time})
#         # Update blend stock levels, considering the task's blend and quantity.
#         blend_code = task['Blend Code']
#         self.blends[blend_code].reduce_stock('production', task['Quantity (kg)'])
#         print(f"Scheduled task {task['SKU Code']} on {line.name} at {start_time}.")

# # Instantiate TransferTimeMatrix with the transfer times data
# transfer_time_matrix = TransferTimeMatrix(updated_parameters_df.set_index('Name'))

# # Instantiate Scheduler with the data from the CSV files
# scheduler = Scheduler(production_schedule_df, rm_availability_df, blend_stock_availability_df, consumption_rates_efficiency_df, transfer_time_matrix)


from deap import base, creator, tools, algorithms
from itertools import cycle
import random
import pandas as pd
from TransferTimeMatrix import TransferTimeMatrix
from ProductionLine import ProductionLine
from Blend import Blend
from Silo import Silo
import numpy

# Assuming TransferTimeMatrix, ProductionLine, Blend, Silo are defined elsewhere as per your project structure

class Scheduler:

    def __init__(self, production_schedule_df, rm_availability_df, blend_stock_availability_df, consumption_rates_efficiency_df, transfer_time_matrix):
        self.production_schedule_df = production_schedule_df
        self.rm_availability_df = rm_availability_df
        self.blend_stock_availability_df = blend_stock_availability_df
        self.consumption_rates_efficiency_df = consumption_rates_efficiency_df
        self.transfer_time_matrix = transfer_time_matrix  # Assuming this is an instance of TransferTimeMatrix

        self.silos = {}
        self.production_lines = {}
        self.blends = {}

        self._initialize_entities()
        self._initialize_ga()

    def _initialize_entities(self):
        for index, row in updated_parameters_df.iterrows():
            self.silos[row['Name']] = Silo(row['Name'], row['Maximum Capacity (kg)'], row['Transfer Type'])

        for index, row in consumption_rates_efficiency_df.iterrows():
            self.production_lines[row['Name']] = ProductionLine(row['Name'], row['Ideal Consumption Rate (kg/h)'], row['Efficiency (%)'])

        for index, row in blend_stock_availability_df.iterrows():
            blend_code = row['Blend Code']
            if blend_code not in self.blends:
                self.blends[blend_code] = Blend(blend_code, row['Blend Description'])
            self.blends[blend_code].add_stock(row['Location'], row['Quantity (kg)'])

        for index, row in rm_availability_df.iterrows():
            silo_name = row['Location']
            blend_code = row['Blend Code']
            quantity = row['Quantity (kg)']
            if silo_name in self.silos:
                self.silos[silo_name].add_stock(blend_code, quantity)

    def _initialize_ga(self):
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)

        self.toolbox = base.Toolbox()
        self.toolbox.register("attr_int", random.randint, 0, len(self.production_schedule_df)-1)
        self.toolbox.register("individual", tools.initRepeat, creator.Individual, self.toolbox.attr_int, n=len(self.production_schedule_df))
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

        self.toolbox.register("evaluate", self.evaluate_individual)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)
        self.toolbox.register("select", tools.selTournament, tournsize=3)

    def evaluate_individual(self, individual):
        # This is where you translate the individual (a list of task indices) into a scheduling decision
        # For simplicity, this is a placeholder. You need to implement this based on your project specifics
        return (1.0,)  # Dummy fitness value

    def optimize_schedule_with_ga(self):
        pop = self.toolbox.population(n=300)
        CXPB, MUTPB, NGEN = 0.5, 0.2, 40

        stats = tools.Statistics(key=lambda ind: ind.fitness.values)
        stats.register("avg", numpy.mean)
        stats.register("std", numpy.std)
        stats.register("min", numpy.min)
        stats.register("max", numpy.max)

        pop, logbook = algorithms.eaSimple(pop, self.toolbox, CXPB, MUTPB, NGEN, stats=stats, verbose=True)

        # Extract and print information about the best solution found
        best_ind = tools.selBest(pop, 1)[0]
        print("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))
        # Additional logic to apply the best scheduling solution to your system

    def decode_individual_to_schedule(self, individual):
        decoded_tasks = [self.production_schedule_df.iloc[idx] for idx in individual]
        # Sort or prioritize tasks based on youpusr criteria, for example, by 'Due Date'
        sorted_tasks = sorted(decoded_tasks, key=lambda x: x['Due Date'])
        # This example simply sorts tasks; you might need a more sophisticated logic here

        # Initialize a schedule for each production line
        schedule = {line_name: [] for line_name in self.production_lines}

        # Assign tasks to lines based on your logic, for a simple round-robin assignment:
        lines_cycle = cycle(self.production_lines.keys())
        for task in sorted_tasks:
            line_name = next(lines_cycle)
            schedule[line_name].append(task)

        return schedule
    
    def print_schedule(self, schedule):
        for line_name, tasks in schedule.items():
            print(f"Schedule for {line_name}:")
            for task in tasks:
                print(f" - Task {task['SKU Code']} scheduled with due date {task['Due Date']}")
            print("\n")



# Load your CSV data here
production_schedule_df = pd.read_csv('production.csv')
rm_availability_df = pd.read_csv('RM.csv')
blend_stock_availability_df = pd.read_csv('blendstock.csv')
consumption_rates_efficiency_df = pd.read_csv('Consumption Rates & Efficiencies of Production Lines-.csv')
updated_parameters_df = pd.read_csv('parameters.csv')

# Assuming transfer_time_matrix is initialized from your transfer times CSV
transfer_time_matrix = TransferTimeMatrix(updated_parameters_df.set_index('Name'))

# Instantiate Scheduler with the data
scheduler = Scheduler(production_schedule_df, rm_availability_df, blend_stock_availability_df, consumption_rates_efficiency_df, transfer_time_matrix)

# Run the GA-based optimization
scheduler.optimize_schedule_with_ga()

# After the GA optimization in main.py or wherever you run the optimization
best_ind = tools.selBest(pop, 1)[0]
print("Best individual is:", best_ind)
print("Best individual's fitness:", best_ind.fitness.values)

# Decode the best individual to a schedule
schedule = scheduler.decode_individual_to_schedule(best_ind)
# Print the decoded schedule
scheduler.print_schedule(schedule)


from deap import base, creator, tools, algorithms
from itertools import cycle
import random
import pandas as pd
from TransferTimeMatrix import TransferTimeMatrix
from ProductionLine import ProductionLine
from Blend import Blend
from Silo import Silo
import numpy

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

    def evaluate_individual(self, individual): return (1.0,)

    def optimize_schedule_with_ga(self):

        pop = self.toolbox.population(n=300)

        CXPB, MUTPB, NGEN = 0.5, 0.2, 40

        stats = tools.Statistics(key=lambda ind: ind.fitness.values)
        # stats.register("avg", numpy.mean)
        # stats.register("std", numpy.std)
        # stats.register("min", numpy.min)
        # stats.register("max", numpy.max)

        pop, logbook = algorithms.eaSimple(pop, self.toolbox, CXPB, MUTPB, NGEN, stats=stats, verbose=False)

        best_ind = tools.selBest(pop, 1)[0]
        schedule = scheduler.decode_individual_to_schedule(best_ind)
        scheduler.print_schedule(schedule)

        print("\n ---------------------------------------------------------- \n")

        print("\n In Conclusion, The Blends Should Undergo This Sequence Based On Their Computed TTC and Fitness Value From The Genetic Algorithm, ", best_ind, "\n\n")

        pd.DataFrame(best_ind).to_csv('logbook.csv', index=False)

        print("\n ----------------------------- Now We Move To The Jupyter Notebook! ----------------------------- \n")

        # self.schedule_to_dataframe(schedule)


        
    def decode_individual_to_schedule(self, individual):

        decoded_tasks = [self.production_schedule_df.iloc[idx] for idx in individual]

        sorted_tasks = sorted(decoded_tasks, key=lambda x: x['Sequence'])

        schedule = {line_name: [] for line_name in self.production_lines}

        lines_cycle = cycle(self.production_lines.keys())

        for task in sorted_tasks:

            line_name = next(lines_cycle)
            line = self.production_lines[line_name]
            qty = task['Quantity (kg)']
            icr = line.consumption_rate
            eff = line.efficiency

            time_to_complete = (qty / (icr * (eff / 100))) * 60

            schedule[line_name].append({

                'task': task,
                'start_time': None,
                'quantity' : task['Quantity (kg)'],
                'time_to_complete': time_to_complete

            })

        return schedule
    
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

            for task in decoded_schedule:

                if task["Location"] == "Warehouse" and task["Transfer Mode"] == "Batch":

                    batch_size = locations_info.get("Warehouse", {}).get("Max Capacity", 0)
                    transfer_time = locations_info.get("Warehouse", {}).get("Transfer Time", 0)

                    if task["Quantity(kg)"] % batch_size != 0:

                        return False

        return True
    
    # def schedule_to_dataframe(self, schedule):
       
    #     data = []

    #     for line_name, tasks in schedule.items():

    #         for task in tasks:

    #             data.append({
    #                 "Line Name": line_name,
    #                 "Blend Code": task['task']['Blend Code'],
    #                 "Quantity": task['quantity'],
    #                 "Time to Complete": task['time_to_complete']
    #             })

    #     pd.DataFrame(data, columns=['Line Name', 'Blend Code', 'Quantity (kg)', 'Time to Complete']).to_csv('logbookFinal.csv', index=False)

    
    
    def print_schedule(self, schedule): 

        data = []


        for line_name, tasks in schedule.items():

            print(f"Schedule for {line_name}:")

            for task in tasks:

                data.append({
                    "Blend Code": task['task']['Blend Code'],
                    "Sequence": task['task']['Sequence'],
                    "Task Duration (Minutes)": task['time_to_complete'] / 60,
                    "Task Duration (Hours)": task['time_to_complete'] / 60 /60,
                    "Quantity" : task['quantity'],
                    "Line To Go To": line_name
                })

                print(f"  Blend {task['task']['Blend Code']}:")
                print(f"    Quantity: {task['quantity']} kg")
                print(f"    Time to complete: {task['time_to_complete']} minutes")
                print("\n")

    
        pd.DataFrame(data, columns=['Blend Code', 'Sequence', 'Task Duration (Minutes)', 'Task Duration (Hours)', 'Quantity', 'Line To Go To']).to_csv('logbookFinal.csv', index=False)



production_schedule_df = pd.read_csv('production.csv')
rm_availability_df = pd.read_csv('RM.csv')
blend_stock_availability_df = pd.read_csv('blendstock.csv')
consumption_rates_efficiency_df = pd.read_csv('Consumption Rates & Efficiencies of Production Lines-.csv')
updated_parameters_df = pd.read_csv('parameters.csv')

transfer_time_matrix = TransferTimeMatrix(updated_parameters_df.set_index('Name'))

scheduler = Scheduler(production_schedule_df, rm_availability_df, blend_stock_availability_df, consumption_rates_efficiency_df, transfer_time_matrix)

scheduler.optimize_schedule_with_ga()
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

        print("\n ----------------------------- Now We Are Off To The Jupyter Notebook To Link The Blends And Visualize Them! ----------------------------- \n")

        
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
                'time_to_complete': time_to_complete

            })

        return schedule
        
    
    def print_schedule(self, schedule):

        for line_name, tasks in schedule.items():

            print(f"Schedule for {line_name}:")

            for task in tasks:

                print(f"  Task {task['task']['SKU Code']}:")
                print(f"    Quantity: {task['task']['Quantity (kg)']} kg")
                print(f"    Time to complete: {task['time_to_complete']} minutes")
                print("\n")


production_schedule_df = pd.read_csv('production.csv')
rm_availability_df = pd.read_csv('RM.csv')
blend_stock_availability_df = pd.read_csv('blendstock.csv')
consumption_rates_efficiency_df = pd.read_csv('Consumption Rates & Efficiencies of Production Lines-.csv')
updated_parameters_df = pd.read_csv('parameters.csv')

transfer_time_matrix = TransferTimeMatrix(updated_parameters_df.set_index('Name'))

scheduler = Scheduler(production_schedule_df, rm_availability_df, blend_stock_availability_df, consumption_rates_efficiency_df, transfer_time_matrix)

scheduler.optimize_schedule_with_ga()
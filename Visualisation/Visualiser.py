
from  EvoAlgs.EvoAnalytics import EvoAnalytics
from Visualisation.ModelVisualization import ModelsVisualization
from CommonUtils.StaticStorage import StaticStorage
from EvoAlgs.BreakersEvo.BreakersEvoUtils import BreakersEvoUtils
from EvoAlgs.BreakersEvo.EvoOperators import WaveHeightObjective,WaveSimulationResult
from Breakers.BreakersUtils import BreakersUtils
import numpy as np

class Visualiser:

    def __init__(self,store_all_individuals,store_best_individuals,num_of_best_individuals_from_population_for_print,model,task):

        self.exp_name = EvoAnalytics.run_id
        self.store_all_individuals=store_all_individuals
        self.store_best_individuals=store_best_individuals
        self.num_of_best_individuals=num_of_best_individuals_from_population_for_print
        self.task=task
        self.model=model


    def print_configuration(self, simulation_result,all_breakers,objective,dir,image_for_gif,num_of_population,ind_num):

        visualiser = ModelsVisualization(str(num_of_population + 1) + "_" + str(ind_num + 1))

        visualiser.simple_visualise(simulation_result.get_5percent_output_for_field(),
                                    all_breakers,
                                    self.model.domain.base_breakers,
                                    StaticStorage.exp_domain.fairways, StaticStorage.exp_domain.target_points,
                                    objective,dir=dir, image_for_gif=image_for_gif,
                                    population_and_ind_number=[num_of_population, ind_num])

        del visualiser


    def print_individuals(self,objectives,num_of_population,simulation_result_store,all_breakers_store,fitnesses=None):

        print("pop num in vis",num_of_population)
        if self.store_best_individuals:
            if StaticStorage.multi_objective_optimization:
                mean_fit=[np.mean(objective) for objective in objectives]
            else:
                mean_fit=fitnesses

            if self.task.goal=="minimization":
                best_for_print=np.argsort(mean_fit)[:self.num_of_best_individuals]
            else:
                best_for_print=np.argsort(mean_fit)[::-1][:self.num_of_best_individuals]
                #best_for_print = [i.genotype.genotype_array for i in sorted(enumerate(objectives), key=lambda fit: np.mean(fit[1]) )[:EvoAnalytics.num_of_best_inds_for_print]]

        if self.store_all_individuals:
            image_for_gif=False
            dir="img"
            for ind_num in range(0,len(simulation_result_store)):

                self.print_configuration(simulation_result_store[ind_num],all_breakers_store[ind_num],objectives[ind_num],dir="img",image_for_gif=False,num_of_population=num_of_population,ind_num=ind_num)


        if self.store_best_individuals:
            for i,ind_num in enumerate(best_for_print):
                self.print_configuration(simulation_result_store[ind_num], all_breakers_store[ind_num], objectives[ind_num], dir="wave_gif_imgs", image_for_gif=True, num_of_population=num_of_population, ind_num=i)



    def print_individ(self,objective,num_of_population,ind_num, simulation_result,all_breakers):
        image_for_gif=False
        dir="img"

        visualiser = ModelsVisualization(str(num_of_population + 1) + "_" + str(ind_num + 1))

        visualiser.simple_visualise(simulation_result.get_5percent_output_for_field(), all_breakers,
                                                self.model.domain.base_breakers,
                                                StaticStorage.exp_domain.fairways, StaticStorage.exp_domain.target_points,
                                                objective, dir=dir, image_for_gif=image_for_gif,
                                                population_and_ind_number=[num_of_population, ind_num])


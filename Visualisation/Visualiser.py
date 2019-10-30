
from  EvoAlgs.EvoAnalytics import EvoAnalytics
from Visualisation.ModelVisualization import ModelsVisualization
from CommonUtils.StaticStorage import StaticStorage

class Visualiser:

    def __init__(self):

        self.exp_name = EvoAnalytics.run_id


    def print_configuration(self, model,simulation_result,all_breakers,num_of_population,fitness,ind_num,dir,image_for_gif):

        print("num_of_pop_and",num_of_population,ind_num)
        visualiser = ModelsVisualization(str(num_of_population + 1) + "_" + str(ind_num + 1))

        visualiser.simple_visualise(simulation_result.get_5percent_output_for_field(), all_breakers,
                                    model.domain.base_breakers,
                                    StaticStorage.exp_domain.fairways, StaticStorage.exp_domain.target_points,
                                    fitness, dir=dir, image_for_gif=image_for_gif,
                                    population_and_ind_number=[num_of_population, ind_num])


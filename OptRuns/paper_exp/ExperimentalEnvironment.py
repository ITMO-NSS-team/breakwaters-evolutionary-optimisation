import datetime
from builtins import staticmethod
import math
from Breakers.Breaker import xy_to_points
from CommonUtils.StaticStorage import StaticStorage
from Computation.СomputationalEnvironment import SwanWinRemoteComputationalManager, SwanWinLocalComputationalManager
from Configuration.Domains import SochiHarbor
from EvoAlgs.BreakersEvo.GenotypeEncoders.AngularEncoder import AngularGenotypeEncoder
from EvoAlgs.BreakersEvo.GenotypeEncoders.CartesianEncoder import CartesianGenotypeEncoder
from EvoAlgs.EvoAnalytics import EvoAnalytics
from EvoAlgs.SPEA2.DefaultSPEA2 import DefaultSPEA2
from Optimisation.Objective import *
from Optimisation.OptimisationTask import OptimisationTask
from Optimisation.Optimiser import ParetoEvolutionaryOptimiser, GreedyParetoEvolutionaryOptimiser, DEOptimiser, \
    GreedyDEOptimiser
from Simulation.WaveModel import SwanWaveModel
from Visualisation.Visualiser import Visualiser, VisualisationSettings, VisualisationData


class ExpCases(Enum):
    single3 = 0
    double3 = 1
    triple1 = 2


class ExpEncoders(Enum):
    cartesian = 0
    angular = 1


class ExpAlgs(Enum):
    multi = 0
    greedy_multi = 1
    verygreedy_multi = 3
    single = 4
    verygreedy_single = 5


class ExperimentalEnvironment:
    selected_modifications_for_tuning1 = [
        Breaker('mod1', list(map(xy_to_points, [[-1, -1], [33, 22], [42, 17]])), 0, 'Ia'),
        Breaker('mod2_top', list(map(xy_to_points, [[-1, -1], [50, 32], [50, 38]])), 0, 'II'),
        Breaker('mod2_bottom', list(map(xy_to_points, [[-1, -1], [50, 39], [50, 38]])), 0, 'II')
    ]

    selected_modifications_for_tuning2 = [
        Breaker('mod1', list(map(xy_to_points, [[-1, -1], [-1, -1], [33, 22], [42, 17]])), 0, 'Ia'),
        Breaker('mod2_top', list(map(xy_to_points, [[-1, -1], [-1, -1], [50, 32], [50, 38]])), 0, 'II'),
        Breaker('mod2_bottom', list(map(xy_to_points, [[-1, -1], [-1, -1], [50, 39], [50, 38]])), 0, 'II')
    ]

    selected_modifications_for_tuning3 = [
        Breaker('mod1', list(map(xy_to_points, [[-1, -1], [-1, -1], [-1, -1], [33, 22], [42, 17]])), 0, 'Ia')
    ]

    @staticmethod
    def _get_modifications_for_experiment(mod_id):
        if isinstance(StaticStorage.exp_domain, SochiHarbor):
            if mod_id == ExpCases.single3:
                return ExperimentalEnvironment.selected_modifications_for_tuning1
            if mod_id == ExpCases.double3:
                return ExperimentalEnvironment.selected_modifications_for_tuning2
            if mod_id == ExpCases.triple1:
                return ExperimentalEnvironment.selected_modifications_for_tuning3
        raise NotImplementedError

    @staticmethod
    def _init_conditions_for_experiment(domain):
        if isinstance(domain, SochiHarbor):
            StaticStorage.is_custom_conditions = True
            StaticStorage.wind = "23.1 135"
            StaticStorage.bdy = "5.3 9.1 200 30"
            StaticStorage.exp_domain = domain

        else:
            raise NotImplementedError

    @staticmethod
    def _get_encoder_for_experiment(enc_id):
        if enc_id == ExpEncoders.cartesian:
            return CartesianGenotypeEncoder()
        if enc_id == ExpEncoders.angular:
            return AngularGenotypeEncoder()
        raise NotImplementedError

    @staticmethod
    def _get_optimiser_for_experiment(enc_id):
        StaticStorage.crossover_type = "SP"

        if enc_id == ExpAlgs.multi:
            return ParetoEvolutionaryOptimiser()
        if enc_id == ExpAlgs.greedy_multi:
            return GreedyParetoEvolutionaryOptimiser()
        if enc_id == ExpAlgs.verygreedy_multi:
            StaticStorage.crossover_type = "I"
            return GreedyParetoEvolutionaryOptimiser()
        if enc_id == ExpAlgs.single:
            return DEOptimiser()
        if enc_id == ExpAlgs.verygreedy_single:
            return GreedyDEOptimiser()
        raise NotImplementedError

    def run_optimisation_experiment(self, task_id, enc_id, algopt_id, run_local, add_label="", is_vis=True):
        if __name__ == 'OptRuns.paper_exp.ExperimentalEnvironment':

            exp_domain = SochiHarbor()

            ExperimentalEnvironment._init_conditions_for_experiment(exp_domain)

            exp_name = f"{str(algopt_id).rsplit('.', 2)[1]}_task-{str(task_id).rsplit('.', 2)[1]}_enc-{str(enc_id).rsplit('.', 2)[1]}"

            EvoAnalytics.run_id = '{add_label}_{exp_name}_{date:%Y_%m_%d_%H_%M_%S}'.format(add_label=add_label,
                                                                                           exp_name=exp_name,
                                                                                           date=datetime.datetime.now())
            EvoAnalytics.clear()

            if run_local:
                computational_manager = SwanWinLocalComputationalManager()
            else:
                computational_manager = SwanWinRemoteComputationalManager(resources_names=["125", "124", "123"])
            wave_model = SwanWaveModel(exp_domain, computational_manager)
            wave_model.model_results_file_name = 'D:\SWAN_sochi\model_results_paper_martech.db'

            optimiser = ExperimentalEnvironment._get_optimiser_for_experiment(algopt_id)

            selected_modifications_for_tuning = ExperimentalEnvironment._get_modifications_for_experiment(task_id)

            if algopt_id == ExpAlgs.single or algopt_id == ExpAlgs.verygreedy_single:
                optimisation_objectives = [
                    RelativeQuailityObjective()]
                analytics_objectives = [
                    RelativeCostObjective(),
                    RelativeNavigationObjective(),
                    RelativeWaveHeightObjective(),
                ]
            else:
                optimisation_objectives = [
                    RelativeCostObjective(),
                    RelativeNavigationObjective(),
                    RelativeWaveHeightObjective()]
                analytics_objectives = [
                    RelativeQuailityObjective()]

            pareto_objectives = [[RelativeWaveHeightObjective(), RelativeCostObjective()]]

            task = OptimisationTask(optimisation_objectives, selected_modifications_for_tuning,
                                    goal="minimise", analytics_objectives=analytics_objectives)

            task.constraints = [(StructuralObjective(), ConstraintComparisonType.equal, 0)]

            StaticStorage.task = task

            StaticStorage.genotype_encoder = ExperimentalEnvironment._get_encoder_for_experiment(enc_id)

            vis_settings = VisualisationSettings(store_all_individuals=is_vis, store_best_individuals=is_vis,
                                                 num_of_best_individuals_from_population_for_print=5,
                                                 create_gif_image=is_vis,
                                                 create_boxplots=is_vis,
                                                 print_pareto_front=is_vis,
                                                 create_pareto_set_chart_during_optimization=is_vis,
                                                 create_boxplots_during_optimization=is_vis,
                                                 create_boxplots_from_history=is_vis)

            vis_data = VisualisationData(optimisation_objectives, base_breakers=exp_domain.base_breakers, task=task,
                                         data_for_pareto_set_chart=pareto_objectives)

            visualiser = Visualiser(vis_settings, vis_data)

            StaticStorage.max_gens = 5
            params = DefaultSPEA2.Params(max_gens=StaticStorage.max_gens, pop_size=5, archive_size=5,
                                         crossover_rate=0.5, mutation_rate=0.5,
                                         mutation_value_rate=[], min_or_max=task.goal)

            optimiser.optimise(wave_model, task, visualiser=visualiser, external_params=params)

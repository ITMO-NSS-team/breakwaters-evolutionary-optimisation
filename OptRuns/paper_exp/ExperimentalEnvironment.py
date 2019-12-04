import datetime
import random
from builtins import staticmethod

from Breakers.Breaker import xy_to_points
from CommonUtils.StaticStorage import StaticStorage
from Computation.СomputationalEnvironment import SwanWinRemoteComputationalManager, SwanWinLocalComputationalManager
from Configuration.Domains import SochiHarbor
from EvoAlgs.BreakersEvo.GenotypeEncoders.GenotypeEncoder import AngularGenotypeEncoder, CartesianGenotypeEncoder
from EvoAlgs.EvoAnalytics import EvoAnalytics
from Optimisation.Objective import *
from Optimisation.OptimisationTask import OptimisationTask
from Optimisation.Optimiser import ParetoEvolutionaryOptimiser, GreedyParetoEvolutionaryOptimiser, DEOptimiser
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
    single = 2
    greedy_single = 3


class ExperimentalEnvironment:
    def __init__(self, seed):
        self.seed = seed

    selected_modifications_for_tuning1 = [
        Breaker('mod1', list(map(xy_to_points, [[-1, -1], [33, 22], [42, 17]])), 0, 'Ia'),
        Breaker('mod2_top', list(map(xy_to_points, [[-1, -1], [50, 32], [50, 39]])), 0, 'II'),
        Breaker('mod2_bottom', list(map(xy_to_points, [[-1, -1], [50, 39], [50, 38]])), 0, 'II')
    ]

    selected_modifications_for_tuning2 = [
        Breaker('mod1', list(map(xy_to_points, [[-1, -1], [-1, -1], [33, 22], [42, 17]])), 0, 'Ia'),
        Breaker('mod2_top', list(map(xy_to_points, [[-1, -1], [-1, -1], [50, 32], [50, 39]])), 0, 'II'),
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
        if enc_id == ExpAlgs.multi:
            return ParetoEvolutionaryOptimiser()
        if enc_id == ExpAlgs.greedy_multi:
            return GreedyParetoEvolutionaryOptimiser()
        if enc_id == ExpAlgs.single:
            return DEOptimiser()
        raise NotImplementedError

    def run_optimisation_experiment(self, task_id, enc_id, algopt_id, run_local):
        if __name__ == 'OptRuns.paper_exp.ExperimentalEnvironment':
            np.random.seed(self.seed)
            random.seed(self.seed)

            exp_domain = SochiHarbor()

            ExperimentalEnvironment._init_conditions_for_experiment(exp_domain)

            exp_name = f"{algopt_id}_task{task_id}_enc{enc_id}"
            EvoAnalytics.clear()
            EvoAnalytics.run_id = 'run_{exp_name}_{date:%Y_%m_%d_%H_%M_%S}'.format(exp_name=exp_name,
                                                                                   date=datetime.datetime.now())
            if run_local:
                computational_manager = SwanWinLocalComputationalManager()
            else:
                computational_manager = SwanWinRemoteComputationalManager(resources_names=["125", "124", "123", "121"])
            wave_model = SwanWaveModel(exp_domain, computational_manager)
            wave_model.model_results_file_name = 'D:\SWAN_sochi\model_results_paper_martech.db'

            optimiser = ExperimentalEnvironment._get_optimiser_for_experiment(algopt_id)

            selected_modifications_for_tuning = ExperimentalEnvironment._get_modifications_for_experiment(task_id)

            optimisation_objectives = [
                RelativeCostObjective(),
                RelativeNavigationObjective(),
                RelativeWaveHeightObjective()]

            analytics_objectives = [
                CostObjective,
                NavigationObjective,
                WaveHeightObjective,
                RelativeQuailityObjective()]

            task = OptimisationTask(optimisation_objectives, selected_modifications_for_tuning,
                                    goal="minimise")
            task.constraints = [(StructuralObjective(), ConstraintComparisonType.equal, 0)]

            StaticStorage.task = task

            StaticStorage.genotype_encoder = ExperimentalEnvironment._get_encoder_for_experiment(enc_id)

            vis_settings = VisualisationSettings(store_all_individuals=False, store_best_individuals=True,
                                                 num_of_best_individuals_from_population_for_print=5,
                                                 create_gif_image=True,
                                                 create_boxplots=True,
                                                 print_pareto_front=True)
            vis_data = VisualisationData(optimisation_objectives, base_breakers=exp_domain.base_breakers, task=task)

            visualiser = Visualiser(vis_settings, vis_data)

            optimiser.optimise(wave_model, task, visualiser=visualiser)

class TestEnvironment(ExperimentalEnvironment):
    def run_optimisation_experiment(self, task_id, enc_id, algopt_id, run_local):
        if __name__ == 'OptRuns.paper_exp.ExperimentalEnvironment':
            np.random.seed(self.seed)
            random.seed(self.seed)

            exp_domain = SochiHarbor()

            ExperimentalEnvironment._init_conditions_for_experiment(exp_domain)

            exp_name = f"test_{algopt_id}_task{task_id}_enc{enc_id}"
            EvoAnalytics.clear()
            EvoAnalytics.run_id = 'run_{exp_name}_{date:%Y_%m_%d_%H_%M_%S}'.format(exp_name=exp_name,
                                                                                   date=datetime.datetime.now())
            if run_local:
                computational_manager = SwanWinLocalComputationalManager()
            else:
                computational_manager = SwanWinRemoteComputationalManager(resources_names=["125", "124", "123", "121"])
            wave_model = SwanWaveModel(exp_domain, computational_manager)
            wave_model.model_results_file_name = 'D:\SWAN_sochi\model_results_paper_martech.db'

            optimiser = ExperimentalEnvironment._get_optimiser_for_experiment(algopt_id)

            selected_modifications_for_tuning = ExperimentalEnvironment._get_modifications_for_experiment(task_id)

            optimisation_objectives = [
                RelativeNavigationObjective(),
                RelativeCostObjective()]

            analytics_objectives = [
                CostObjective,
                NavigationObjective,
                WaveHeightObjective,
                RelativeQuailityObjective()]

            task = OptimisationTask(optimisation_objectives, selected_modifications_for_tuning,
                                    goal="minimise")
            task.constraints = [(StructuralObjective(), ConstraintComparisonType.equal, 0)]

            StaticStorage.task = task

            StaticStorage.genotype_encoder = ExperimentalEnvironment._get_encoder_for_experiment(enc_id)

            vis_settings = VisualisationSettings(store_all_individuals=False, store_best_individuals=True,
                                                 num_of_best_individuals_from_population_for_print=5,
                                                 create_gif_image=True,
                                                 create_boxplots=True,
                                                 print_pareto_front=True)
            vis_data = VisualisationData(optimisation_objectives, base_breakers=exp_domain.base_breakers, task=task)

            visualiser = Visualiser(vis_settings, vis_data)

            opt_res = optimiser.optimise(wave_model, task, visualiser=visualiser)
            print("Final result")
            print(opt_res.history[19][0].genotype.get_parameterized_chromosome_as_num_list())
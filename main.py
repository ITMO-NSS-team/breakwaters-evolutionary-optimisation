from Configuration.Harbor import SochiHarbor
from Simulation.WaveModel import SimpleGeomWaveModel
from Optimisation.Optimiser import ManualOptimiser, StubOptimiser
exp_domain = SochiHarbor()


wave_model = SimpleGeomWaveModel(exp_domain)

optimiser = StubOptimiser()
opt_result = optimiser.optimise(wave_model)

hs0 = opt_result.simulation_result.get_output_for_target_point(exp_domain.target_points[0])

print(hs0)

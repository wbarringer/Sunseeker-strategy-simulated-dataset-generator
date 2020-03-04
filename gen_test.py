# Test of data artificial data generation tools

import GenTools

mass = 700  # Mass of the car in lbs

sim = GenTools.DataGenerator(sim_time=5, logging=False)

sim.run_route_based("route.json")
print(sim.Battery.high_cell)
print(sim.Battery.low_cell)
# sim.run()

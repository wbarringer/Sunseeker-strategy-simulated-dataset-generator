# Test of data artificial data generation tools

import GenTools

mass = 700  # Mass of the car in lbs

Array = GenTools.Array()
Battery = GenTools.Battery(35, 12, 3300)
Sun = GenTools.Sun()
Motor = GenTools.Motor(mass)
sim = GenTools.DataGenerator(Array, Battery, Sun, Motor, sim_time=5)

sim.run_route_based("route.json")
# sim.run()

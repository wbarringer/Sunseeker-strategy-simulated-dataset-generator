# Test of data artificial data generation tools

import GenTools

mass = 700  # Mass of the car in lbs

Array = GenTools.Array()
Battery = GenTools.Battery(35, 12, 3300)
Sun = GenTools.Sun()
Motor = GenTools.Motor(mass / 2.2)
sim = GenTools.DataGenerator(Array, Battery, Sun, Motor, sim_time=5)


sim.accelerate(12)
# sim.run()
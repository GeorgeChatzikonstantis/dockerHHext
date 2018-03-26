#!/usr/bin/env python 

import sys
sys.path.insert(0, '/home/georgec/docker_playground/pyNN_dev')
print(sys.path)
import pyNN.brainframe as sim

sim.setup()
pop=sim.Population(96, sim.HH_cond_exp(i_offset=0.6 ), label="HH_cond_exp")
syn = sim.StaticSynapse(weight=0.04, delay=0)
prj = sim.Projection(pop, pop, sim.FixedProbabilityConnector(0.25, allow_self_connections=False), syn)
sele = sim.Backend_selector(prj,'PHI')
selected = sele.select_backend()
corw = sim.Sim_core(selected,prj,'/home/georgec/docker_playground/pyNN_dev/pyNN/brainframe/sim_core.ini')
corw.run_sim_core(simtime=100,run_id='0dmhCK6GhYp_haSqAAAO')

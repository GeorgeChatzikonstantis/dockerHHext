#!/usr/bin/env python 

import sys
sys.path.insert(0, '/app/dockerHHext')
print(sys.path)
import pyNN.brainframe as sim

print("Setup...")
sim.setup()
print("Setup Done...")
pop=sim.Population(960, sim.HH_cond_exp(i_offset=0.6 ), label="HH_cond_exp")
syn = sim.StaticSynapse(weight=0.04, delay=0)
prj = sim.Projection(pop, pop, sim.FixedProbabilityConnector(0.25, allow_self_connections=False), syn)
print("Network Built...")

sele = sim.Backend_selector(prj,'XEON')
selected = sele.select_backend()
corw = sim.Sim_core(selected,prj,'/app/dockerHHext/pyNN/brainframe/sim_core.ini')
print("Xeon Backend Selected...")
print("Running...")
corw.run_sim_core(simtime=1000)

sele = sim.Backend_selector(prj,'PHI')
selected = sele.select_backend()
corw = sim.Sim_core(selected,prj,'/app/dockerHHext/pyNN/brainframe/sim_core.ini')
print("Phi Backend Selected...")
print("*THIS WILL PROBABLY CRUSH*")
print("Running...")
corw.run_sim_core(simtime=1000)

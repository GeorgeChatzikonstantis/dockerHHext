from pyNN import common
import subprocess
import os.path
from pyNN.infoli.cells import NativeCellType
name = "InfoliSimulator"


class ID(int, common.IDMixin):

    def __init__(self, n):
        """Create an ID object with numerical value `n`."""
        int.__init__(n)
        common.IDMixin.__init__(self)


class State(common.control.BaseState):

    def __init__(self):
        common.control.BaseState.__init__(self)
        print("Lele init sim")
        self.mpi_rank = 0
        self.num_processes = 1
        self.clear()
        self.dt = 0.1

    def run(self, simtime):
        print("Lele")
        self.t += simtime
        self.running = True

    def run_until(self, tstop):
        print("Leleuntil")
        self.t = tstop
        cmdtest=['/home/harry/Dropbox/infoli/stored_results/local/test1.sh']
        cmdtest.append('-network_size')
        cmdtest.append(str(self.neuronum))
        cmdtest.append('-sim_time')
        cmdtest.append(str(self.t))
        cmdtest.append('-connectivity_map')

        if os.path.isfile('cellConnections.txt'):
            cmdtest.append('cellConnections.txt')
        else:
            print("No connectivity map")
            exit()
        print(cmdtest)
        outputtest = subprocess.check_output(cmdtest)
        print(outputtest.decode('unicode_escape'))
        self.running = True

    def clear(self):
        self.recorders = set([])
        self.id_counter = 42
        self.segment_counter = -1
        self.reset()

    def reset(self):
        """Reset the state of the current network to time t = 0."""
        self.running = False
        self.t = 0
        self.t_start = 0
        self.segment_counter += 1

state = State()

class SimpleNeuron(object):

    def __init__(self, **parameters):
        
        
        self.soma = Secscs(L=600, diam=2, nseg=5, Ra=100, v=-65.0, ref_v=70.0)

        # needed for PyNN
        self.source_section = self.soma
        self.source = self.soma['ref_v']
        self.parameter_names = ('g_leak', 'gnabar', 'gkbar')
        self.traces = {}
        self.recording_time = False
    
    def memb_init(self):
        for seg in self.soma:
            seg.v = self.v

class SimpleNeuronType(NativeCellType):
    default_parameters = {'g_leak': 0.0002, 'gkbar': 0.036, 'gnabar': 0.12}
    default_initial_values = {'v': -65.0}
    recordable = ['soma.v']
    units = {'soma.v' : 'mV'}
    #receptor_types = ['soma.cm']
    model = SimpleNeuron

# mock section
class Secscs(object):
    def __init__(self, L, diam, nseg, Ra, v, ref_v):
        # set geometry
        self.L = L
        self.diam = diam
        self.nseg = nseg
        # set cable properties
        self.Ra = Ra
        #self.cm = cm
        self.v = v
        self.ref_v= ref_v



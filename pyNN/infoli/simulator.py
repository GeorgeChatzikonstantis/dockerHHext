from pyNN import common
import subprocess
import os.path
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

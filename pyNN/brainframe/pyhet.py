from pyNN import common
import os.path
import configparser
import subprocess
from . import simulator
from .projections import Projection

class Backend_selector: #Selecting appropriate simulation platform
    blist=["phi","dfe","gpu"] #list of platforms
    bselection=0

    def __init__(self, mode):
        self.mode = mode

    def print_modes(self): # print all modes
        i=0
        print("a\t=> Automatic Selection")
        for x in Backend_selector.blist:
            print(i,"\t=> ",Backend_selector.blist[i])
            i+=1
        print("<------->")

    def print_mode(self): # print current mode
        tmp=str(Backend_selector.blist[self.mode])
        print(tmp,"\n")

#Selecting an appropriate platform for backend
# It selects either manually, or automatically from network density and neuron number
    def select_backend(self, num_of_neurons=0, num_of_connections=0):
        if self.mode!="a":
            return Backend_selector.blist[self.mode]
        elif (num_of_neurons<2 and num_of_connections < 2):
            raise ValueError('Number of neurons and connections too small...')
        else:
            density=num_of_connections/(num_of_neurons*(num_of_neurons-1))
            print("Density of the network: ",density)
            print("Number on neurons: ", num_of_neurons)
            if (num_of_neurons>=4000):
                Backend_selector.bselection=2 #GPU
            elif (density>=0.85 and num_of_neurons<4000):
                Backend_selector.bselection=1 #DFE
            elif (density<0.85 and num_of_neurons<900):
                Backend_selector.bselection=1 #DFE
            else:
                Backend_selector.bselection=0 #PHI
            print("Original Selection: ", Backend_selector.blist[Backend_selector.bselection])

            if Backend_selector.bselection==2: # currently we don'thave GPUs
                Backend_selector.bselection=1

            tmp2=Backend_selector.bselection
            return Backend_selector.blist[tmp2]

# Sim_core is the main class that deals with the communication between webserver and the
# accelerator
class Sim_core(Projection):

    def __init__(self, platform, prj, conf_file="sim_core.ini"):
        self.platform= platform
        self.conf_file=conf_file
        self.prj=prj
        self.config = configparser.ConfigParser()
        self.config.read(conf_file)
        self.ip = self.config.get("Server","IP")
        self.user = self.config.get("Server","user")
        self.outputpath= self.config.get("Paths","outputpath")

    def print_conf(self):
        print("Server:")
        for key in self.config['Server']:
            print(key,"\t\t:",self.config.get("Server",key))
        print("Paths:")
        for key in self.config['Paths']:
            print(key,"\t:",self.config.get("Paths",key))

    def print_platform(self):
        print(self.platform)

    def check_communication(self):
        cmd_ping = "ping -q -c 1 "+self.ip+" > /dev/null"
        cmd_ssh= "ssh -q "+self.user+"@"+self.ip+" exit"
        print(cmd_ssh)
        print(cmd_ping)
        online_flag = subprocess.call(cmd_ping, shell=True)
        if online_flag==0:
            print("Server Online!")
        else:
            print("Cannot reach server!")
        connect_flag= subprocess.call(cmd_ssh, shell=True)
        if connect_flag==0:
            print("Connection ok!")
        else:
            print("Cannot connect to server!")


    def get_status(self):
        cmd_ssh= "ssh -q "+self.user+"@"+self.ip+" cat "+self.outputpath+"/state"
        print(cmd_ssh)
        state = subprocess.check_output(cmd_ssh, shell=True)
        print(str(state))
        f = open('state', 'w')
        f.write(str(state))
        f.close()

    def run_sim_core(self):
        self.get_status()
        # If status is free must add here
        net_size=len(self.prj.post)
        # The parameters later must be expand for all cases
        dictt=self.prj.synapse_type.describe(template=None)
        dictt['parameters']['weight'].shape=(1,1)
        dictt['parameters']['delay'].shape=(1,1)
        weight=dictt['parameters']['weight'][0][0]
        delay=dictt['parameters']['delay'][0][0]
        dicon=self.prj._connector.describe(template=None)
        probability=dicon['parameters']['p_connect']

        str_to_send=" -net_size "+str(net_size)+" -probability "+str(probability)
        print(str_to_send)
        return str_to_send



        




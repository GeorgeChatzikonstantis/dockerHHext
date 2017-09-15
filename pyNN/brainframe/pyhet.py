from pyNN import common
import os.path
import os
import configparser
import subprocess
import time
import string
import re
from . import simulator
from .projections import Projection

class Backend_selector(Projection): #Selecting appropriate simulation platform
    blist=["PHI","DFE","GPU"] #list of platforms
    bselection=0
    

    def __init__(self, prj, mode):
        self.mode = mode
        self.prj = prj

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
    def select_backend(self):
        if self.mode!="a":
            return self.mode
        #elif (num_of_neurons<2 and num_of_connections < 2):
        #    raise ValueError('Number of neurons and connections too small...')
        else:
            num_of_neurons=len(self.prj.post)
            dicon=self.prj._connector.describe(template=None)
            density=dicon['parameters']['p_connect']
            print("Density of the network: ",density)
            print("Number on neurons: ", num_of_neurons)
            if (num_of_neurons>=3500):
                Backend_selector.bselection=0 #PHI
            else:
                Backend_selector.bselection=1 #DFE
            print("Original Selection: ", Backend_selector.blist[Backend_selector.bselection])


            tmp2=Backend_selector.bselection
            return Backend_selector.blist[tmp2]

# Sim_core is the main class that deals with the communication between webserver and the
# accelerator
class Sim_core(Projection):

    def __init__(self, platform, prj, conf_file="sim_core.ini-hartree"):
        self.platform= platform
        self.conf_file=conf_file
        self.prj=prj
        self.config = configparser.ConfigParser()
        self.config.read(conf_file)
        if self.platform == "PHI":
            self.ip = self.config.get("PHI","IP")
            self.user = self.config.get("PHI","user")
            self.executable = self.config.get("PHI","executable")
            self.runpath = self.config.get("PHI","runpath")
            self.statepathclient = self.config.get("PHI","statepathclient")
            self.statepathserver = self.config.get("PHI","statepathserver")
        elif self.platform == "DFE":
            self.ip = self.config.get("DFE","IP")
            self.user = self.config.get("DFE","user")
            self.executable = self.config.get("DFE","executable")
            self.runpath = self.config.get("DFE","runpath")
            self.statepathserver = self.config.get("DFE","statepathserver")
            self.statepathclient = self.config.get("DFE","statepathclient")
        else:
            raise ValueError('Unrecognized platform')


    def print_conf(self):
        print("PHI:")
        for key in self.config['PHI']:
            print(key,"\t\t:",self.config.get("PHI",key))
        print("DFE:")
        for key in self.config['DFE']:
            print(key,"\t:",self.config.get("DFE",key))

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
        cmd_ssh= "ssh -q "+self.user+"@"+self.ip+" cat "+self.statepathserver
        print(cmd_ssh)
        state = subprocess.check_output(cmd_ssh, shell=True)
        print(str(state))
        f = open(self.statepathclient, 'w')
        f.write(str(state))
        f.close()
        return state

    def set_status(self,status):
        strr=status
        cmd_ssh= "ssh -q "+self.user+"@"+self.ip+" \'echo "+strr+">"+self.statepathserver+"\'"
        print(cmd_ssh)
        state = subprocess.check_output(cmd_ssh, shell=True)
        print(strr)
        f = open(self.statepathclient, 'w')
        f.write(str(strr))
        f.close()

    def run_sim_core(self,simtime=1000,run_id='tmp22'):
        net_size=len(self.prj.post)
        sim_time = str(simtime)
        stat = str(self.get_status())
        flag='free'
        while flag not in stat:
            time.sleep(2)
            stat = str(self.get_status())
            print(stat)

        self.set_status("busy")


        # The parameters later must be expand for all cases
        dictt=self.prj.synapse_type.describe(template=None)
        dictt['parameters']['weight'].shape=(1,1)
        dictt['parameters']['delay'].shape=(1,1)
        weight=dictt['parameters']['weight'][0][0]
        delay=dictt['parameters']['delay'][0][0]
        dicon=self.prj._connector.describe(template=None)
        probability=dicon['parameters']['p_connect']

        str_to_send="ssh -t -t "+self.user+"@"+self.ip+" "+self.executable+" -net_size "
        str_to_send+=str(net_size)+" -probability "+str(probability)+" -sim_time "+sim_time
        str_to_send+=" -dir "+run_id
        outs = subprocess.check_output(str_to_send, shell=True)

        print(str_to_send)
        tmp=outs.decode("utf-8") 
        output_list=tmp.split('\n')
        exec_time=''
        sim_output=''
        write_flag=0
        for line in output_list:
            if re.search('execution time',line, re.IGNORECASE):
                exec_time=line
            if re.search('runtime',line, re.IGNORECASE):
                exec_time=line
            if write_flag==1:
                sim_output+=line
            if 'output_start' in line:
                write_flag=1
            if 'output_stop' in line:
                write_flag=0

        print(exec_time)
        print("---------------")
        print(sim_output)
        
        f = open("stats.txt", 'w')
        f.write(exec_time)
        f.close()
        ttmp='\n'.join(sim_output[i:i+86] for i in range(0, len(sim_output), 86))
        g = open("sim_output.txt", 'w')
        g.write(ttmp)
        g.close()


        #print(str(outs))
        self.set_status("free")

        return str_to_send



        




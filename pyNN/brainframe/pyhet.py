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
                Backend_selector.bselection=2
            elif (density>=0.85 and num_of_neurons<4000):
                Backend_selector.bselection=1
            elif (density<0.85 and num_of_neurons<900):
                Backend_selector.bselection=1
            else:
                Backend_selector.bselection=0
            print("Original Selection: ", Backend_selector.blist[Backend_selector.bselection])

            if Backend_selector.bselection==2: # currently we don'thave GPUs
                Backend_selector.bselection=1

            tmp2=Backend_selector.bselection
            return Backend_selector.blist[tmp2]


"""
Created on Dec 2, 2011

@author: achernetz
"""
import wx

class Simulator(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        self.Panel = SimulatorPanel(self)
        self.Fit()

    def OnQuit(self, event=None):
        self.Close()

class SimulatorPanel(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)
        
        self.parent = parent
        
        
"""
Class to encapsulate a parameter being sent to the simulator.
"""
class SimulationParameter(object):
    def __init__(self, name, value, desc=None):
        self.name = name
        self.value = value
        self.desc = desc
    
    def __str__(self):
        paramStr = "{0} : {1}\n{2}".format(self.name, self.value, self.desc)
        return paramStr
    
    def __repr__(self):
        return self.__str__()


class Listener(object):
    def __init__(self, id, action):
        self.id = id
        self.action = action

"""
Class to define a market simulator being run on some set of parameters.
"""
class Simulator(object):
    
    def addStatusListener(self, listener):
        self._statusListeners[listener.id] = listener
    
    def getParameter(self, key):
        for param in self._params:
            if param.name == key:
                return param.value
        return None
    

    def __init__(self, simParams):
        self._params = [].extend(simParams)
        self._eventStatus = "Ready to simulate"
        self._statusListeners = {}
    
    def run(self):
        self._eventStatus("Running the simulator...")
        
        
                
    
class MyClass(object):
    '''
    classdocs
    ''' 


    def __init__(selfparams):
        '''
        Constructor
        '''
        
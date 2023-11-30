# utils.py
import os

def makeModelFileMessage(modelPath):
        existsVis = True
        notVis = False
        if os.path.exists(modelPath):
            # figure out a way to elegantly make a new model
            modelMessage = 'Create a model.\nModel file exits at: ' + modelPath + ' Use this model?'
            existsVis = True #model exists
            notVis = False
        else:
            modelMessage = 'Create a model.\nNo model available at ' + modelPath + 'Click okay to create a new one.'
            existsVis = False
            notVis = True
        return modelMessage, existsVis, notVis   
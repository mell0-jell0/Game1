from utility import *
class Action:
    '''
    Class for maintaining information about different kinds of actions for the purposes of user interaction
    Has image icons to indicate whether or not the action is available and a description of the action as well
    '''
    def __init__(self, availableImg, unavailableImg, description):
        self.availableImg = availableImg
        self.unavailableImg = unavailableImg
        self.description = description

attackAction = Action(load_image("attackAvailableIcon.png", scale=1)[0], 
                      load_image("attackUnavailableIcon.png", scale=1),
                      "Attack target")
interactAction = Action(load_image("interactAvailableIcon.png", scale=1),
                        load_image("interactUnavailableIcon.png", scale=1),
                        "Interact with this object")
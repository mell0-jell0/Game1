from utility import *
class Action:
    '''
    Class for maintaining information about different kinds of actions for the purposes of user interaction
    Has image icons to indicate whether or not the action is available and a description of the action as well
    '''
    def __init__(self, availableImg: tuple[pg.surface.Surface, pg.rect.Rect], unavailableImg, buttonWord, description):
        self.availableImg = availableImg
        self.unavailableImg = unavailableImg
        self.description = description
        self.buttonWord = buttonWord

        availButtonTextImg = TextImg(buttonWord, "white", pg.color.Color(30,30,30,150), self.availableImg[0].get_rect().height)
        unavailButtonTextImg = TextImg(buttonWord, "grey", "black", self.unavailableImg[0].get_rect().height)
        availButtonWidth = availableImg[0].get_rect().width + availButtonTextImg.image.get_rect().width
        availButtonHeight = availableImg[0].get_rect().height
        unavailButtonWidth = unavailableImg[0].get_rect().width + unavailButtonTextImg.image.get_rect().width
        unavailButtonHeight = unavailableImg[0].get_rect().height

        self.availableButton = pg.surface.Surface((availButtonWidth, availButtonHeight))
        self.availableButton.blit(*availableImg)
        #blit text next to the icon with same height
        self.availableButton.blit(availButtonTextImg.image, (0+availableImg[0].get_rect().width,0))
        self.unavailableButton = pg.surface.Surface((unavailButtonWidth, unavailButtonHeight))
        self.unavailableButton.blit(*unavailableImg)
        self.unavailableButton.blit(unavailButtonTextImg.image, (0+unavailableImg[0].get_rect().width,0))

attackAction = Action(load_image("attackAvailableIcon.png", scale=1), 
                      load_image("attackUnavailableIcon.png", scale=1),
                      "Attack",
                      "Attack target")
interactAction = Action(load_image("interactAvailableIcon.png", scale=1),
                        load_image("interactUnavailableIcon.png", scale=1),
                        "Interact",
                        "Interact with this object")
'''We want to be able to check through the components to see if there is an action there. modularly add functionality. if the component has associated action then add that action as a possibility to the popup menu and to the actions that could be resolved'''
TODO: fix click handling so that path is not cleared if a pathwalk is active.
TODO: add turn stepping
TODO: do a consistency pass. Make functions act on objects consistently, make formatting consistent. are surfaces passed around, are (surface, rect) tuples passed around? where is the rect updated? I want to be able to use groups so the rects for the images need to be updated correctly.
TODO: turn taking
    when its a players turn we need to be listening in the process function. When it is an NPC's turn we need to be operating in the update function. we need to handle multi-frame-processes in both of these functions.

    Theory:
        Turns are atomic units of time; a character action takes 1 or more units of time. If a player starts a long (multi-turn) action I don't know if I want them to be able to stop in the middle or not. Being able to stop in the middle could make it less frustrating as you won't get punished as hard for tactical missteps. On the other side, not allowing the player to stop in the middle of an action means that players have to make more meaningful decisions. I could of course mix these two approaches and have certain actions of each type. Movement to a distant tile could be interrupted while throwing a grenade for example cant be stopped after the pin is pulled.
    
    I also think that I want to 

    turntakers can have a current active action.

    keep track of turntakers and whose turn it is. end and iterate through turns correctly. handle multi turn actions.

    walking, shooting, looting

    every action has a turn cost. Simple actions take fewer turns while more complicated or involved actions take more turns. shooting, walking, 
TODO: find a way to document actions like that path walk that may get hidden in code.
NOTE: A problem I have now is that its a little bit unelegant and a pain in the dick to chop the path into multiple parts. it is made worse so by the fact that the scheme I have been using thus far has included source nodes. This means that the source and destination nodes of the next and previous paths overlap.
TODO: add code to make path walking arrow always point in correct direction.
TODO: rework the architecture. Make the turn handling information passing less complicated.
TODO: rework how the turnEnd function is passed around.
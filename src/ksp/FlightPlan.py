import sys
sys.path.append(".")


from dataclasses import dataclass
from ksp.Misc.Stages import STAGES, Stage
from ksp.Misc.DataClasses import Mission
from typing import Protocol
from enum import Enum


class Situation(Enum):
    """ Enumerate the situation a vessel is in.
    """
    PRE_LAUNCH = "pre_launch"
    FLYING = "flying"
    ESCAPING = "espcaping"
    ORBITING = "orbiting"
    DOCKED = "docked"
    SUB_ORBITAL = "sub_orbital"
    LANDED = "landed"
    SPLASHED = "splashed"


class Context(Protocol):
    """ Context menu on the situation a vessel is in.
    """
    def __init__(conn, messager, vessel, ap, fp):
        ...

    def display_actions():
        ...

    def get_action(choice):
        ...

class PreLaunch(Context):
    def __init__(self, conn, messager, vessel, ap, fp):
        self.conn = conn
        self.messager = messager
        self.vessel = vessel
        self.ap = ap
        self.fp = fp

    """ pre_launch - Vessel is awaiting launch. """

    def display_actions(self):
        return ["exit", "pre-launch", f"{self.vessel.name} launch"]

    def get_action(self, choice: str):
        CHOICE = {"1": STAGES[Stage.PRE_LAUNCH](self.conn, self.messager, self.vessel, self.ap,self.fp),
                  "2": STAGES[Stage.LAUNCH](self.conn, self.messager, self.vessel, self.ap,self.fp),
                  "0": None, }
        try:                  
            selected = CHOICE[choice]
        except:
            print(f"""
            #####################################
                {choice} is not a valid choice
            #####################################
            """)
            selected= None
        return selected


class Flying(Context):
    def __init__(self, conn, messager, vessel, ap, fp):
        self.conn = conn
        self.messager = messager
        self.vessel = vessel
        self.ap = ap
        self.fp = fp

    """ flying - Vessel is flying through an atmosphere. """
    def display_actions(self):
        return ["exit","land"]

    def get_action(self, choice: str):
        CHOICE = {"0": None, "1": STAGES[Stage.LAND](self.conn, self.messager, self.vessel, self.ap,self.fp),}
        try:                  
            selected = CHOICE[choice]
        except:
            print(f"""
            #####################################
                {choice} is not a valid choice
            #####################################
            """)
            selected= None
        return selected


class Escaping(Context):
    def __init__(self, conn, messager, vessel, ap, fp):
        self.conn = conn
        self.messager = messager
        self.vessel = vessel
        self.ap = ap
        self.fp = fp
    """ escaping - Escaping. """
    def display_actions(self):
        return ["exit"]

    def get_action(self, choice: str):
        CHOICE = {"0": None,"1": STAGES[Stage.ORBIT](self.conn, self.messager, self.vessel, self.ap,self.fp), }
        try:                  
            selected = CHOICE[choice]
        except:
            print(f"""
            #####################################
                {choice} is not a valid choice
            #####################################
            """)
            selected= None
        return selected


class Orbiting(Context):
    def __init__(self, conn, messager, vessel, ap, fp):
        self.conn = conn
        self.messager = messager
        self.vessel = vessel
        self.ap = ap
        self.fp = fp
    """  orbiting - Vessel is orbiting a body. """
    def display_actions(self):
        return ["exit","orbit","land"]

    def get_action(self, choice: str):
        CHOICE = {"0": None, "1": STAGES[Stage.ORBIT](self.conn, self.messager, self.vessel, self.ap,self.fp),"3": STAGES[Stage.LAND](self.conn, self.messager, self.vessel, self.ap,self.fp),}
        try:                  
            selected = CHOICE[choice]
        except:
            print(f"""
            #####################################
                {choice} is not a valid choice
            #####################################
            """)
            selected= None
        return selected


class Docked(Context):
    def __init__(self, conn, messager, vessel, ap, fp):
        self.conn = conn
        self.messager = messager
        self.vessel = vessel
        self.ap = ap
        self.fp = fp
    """  docked  - Vessel is docked to another. """
    def display_actions(self):
        return ["exit"]

    def get_action(self, choice: str):
        CHOICE = {"0": None, "1": STAGES[Stage.ORBIT](self.conn, self.messager, self.vessel, self.ap,self.fp),}
        try:                  
            selected = CHOICE[choice]
        except:
            print(f"""
            #####################################
                {choice} is not a valid choice
            #####################################
            """)
            selected= None
        return selected


class SubOrbital(Context):
    def __init__(self, conn, messager, vessel, ap, fp):
        self.conn = conn
        self.messager = messager
        self.vessel = vessel
        self.ap = ap
        self.fp = fp
    """  sub_orbital - Vessel is on a sub-orbital trajectory. """
    def display_actions(self):
        return ["exit","orbit","sub_orbit","land"]

    def get_action(self, choice: str):
        CHOICE = {"0": None,"1": STAGES[Stage.ORBIT](self.conn, self.messager, self.vessel, self.ap,self.fp),"2": STAGES[Stage.DEORBIT](self.conn, self.messager, self.vessel, self.ap,self.fp), "3": STAGES[Stage.LAND](self.conn, self.messager, self.vessel, self.ap,self.fp),}
        try:                  
            selected = CHOICE[choice]
        except:
            print(f"""
            #####################################
                {choice} is not a valid choice
            #####################################
            """)
            selected= None
        return selected


class Landed(Context):
    def __init__(self, conn, messager, vessel, ap, fp):
        self.conn = conn
        self.messager = messager
        self.vessel = vessel
        self.ap = ap
        self.fp = fp
    """  landed - Vessel is landed on the surface of a body. """
    def display_actions(self):
        return ["exit"]

    def get_action(self, choice: str):
        CHOICE = {"0": None}
        try:                  
            selected = CHOICE[choice]
        except:
            print(f"""
            #####################################
                {choice} is not a valid choice
            #####################################
            """)
            selected= None
        return selected


class Splashed(Context):
    def __init__(self, conn, messager, vessel, ap, fp):
        self.conn = conn
        self.messager = messager
        self.vessel = vessel
        self.ap = ap
        self.fp = fp
    """  splashed - Vessel has splashed down in an ocean. """
    def display_actions(self):
        return ["exit"]

    def get_action(self, choice: str):
        CHOICE = {"0": None, }
        try:                  
            selected = CHOICE[choice]
        except:
            print(f"""
            #####################################
                {choice} is not a valid choice
            #####################################
            """)
            selected= None
        return selected




class FlightContext(object):
    def __init__(self, conn, messager, vessel, ap, fp):
        self.conn = conn
        self.messager = messager
        self.vessel = vessel
        self.ap = ap
        self.fp = fp
        self.FLIGHT = {
            Situation.PRE_LAUNCH: PreLaunch(self.conn, self.messager, self.vessel, self.ap, self.fp),
            Situation.FLYING: Flying(self.conn, self.messager, self.vessel, self.ap,self.fp),
            Situation.ESCAPING: Escaping(self.conn, self.messager, self.vessel, self.ap,self.fp),
            Situation.ORBITING: Orbiting(self.conn, self.messager, self.vessel, self.ap,self.fp),
            Situation.DOCKED: Docked(self.conn, self.messager, self.vessel, self.ap,self.fp),
            Situation.SUB_ORBITAL: SubOrbital(self.conn, self.messager, self.vessel, self.ap,self.fp),
            Situation.LANDED: Landed(self.conn, self.messager, self.vessel, self.ap,self.fp),
            Situation.SPLASHED: Splashed(self.conn, self.messager, self.vessel, self.ap,self.fp),
        }

    def get_context(self, context):
        return self.FLIGHT[context]


class FlightPlanFactory():
    pass
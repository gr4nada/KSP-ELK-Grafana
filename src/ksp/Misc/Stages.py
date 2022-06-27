from pickle import TRUE
import sys
sys.path.append("..")

import asyncio
from enum import Enum
from typing import Any,Protocol
from ksp.Misc.Telemetry import KStream,TELEMETRY, Telemetries, Telemetry
from ksp.Misc.Maneuvers import ManeuverNode


class Stage(Enum):
    PRE_LAUNCH = "pre_launch"
    LAUNCH = "launch"
    DEORBIT = "deorbit"
    ORBIT = "orbit"
    LAND = "land"
    DISCARD = "discard"

class Stages(Protocol):
    def __init__(self, conn:Any, mensseger:Any, vessel:Any, ap:Any, fp:Any):
        ...

    async def task():
        ...

    def get_telemetry():
         ...

class StagePreLaunch(Stages):
    def __init__(self, conn:Any,mensseger:Any, vessel:Any, ap:Any, fp:Any):
        self.conn=conn
        self.mensseger=mensseger
        self.vessel = vessel
        self.ap = ap
        self.heading = fp["heading"]
        self.parts:Telemetry = TELEMETRY[Telemetries.PART](self.conn)
        self.resources:Telemetry = TELEMETRY[Telemetries.RESOURCE](self.conn)


    def get_telemetry(self):
        print(self.parts.get_telemetry())
        print(self.resources.get_telemetry())

    async def task(self, flight_plan):
    # async def task(self):
        self.mensseger.msg("Executing Prelaunch")
        self.desired_heading = self.heading
        self.vessel.control.sas = True # Is this ok?
        self.vessel.control.rcs = False
        self.vessel.control.throttle = 1
        self.ap.reference_frame = self.vessel.surface_reference_frame
        self.ap.target_pitch_and_heading(90, self.desired_heading)
        self.ap.target_roll = float('nan')
        self.ap.engage()
        self.get_telemetry()

class StageLaunch(Stages):
    def __init__(self,conn:Any, mensseger:Any, vessel:Any, ap:Any, fp:Any):
        self.conn=conn
        self.mensseger=mensseger
        self.vessel = vessel
        self.ap = ap
        self.desired_heading = fp["heading"]
        self.desired_altitude = 0
        self.turn_start_altitude = 120.0
        self.turn_mid_altitude = self.vessel.orbit.body.atmosphere_depth * 0.60
        self.turn_end_altitude = self.vessel.orbit.body.atmosphere_depth * 0.80
        self.attr = {}
        self.attr["altitude"] = KStream(self.conn, self.vessel.flight(), 'mean_altitude')
        self.attr["apoapsis"] = KStream(self.conn, self.vessel.orbit, 'apoapsis_altitude')
        self.nav:Telemetry = TELEMETRY[Telemetries.NAV](self.conn)

    def get_telemetry(self):
        print(self.nav.get_telemetry())

    def _proportion(self, val, start, end):
        return (val - start) / (end - start)

    async def task(self, fp):
        self.mensseger.msg("Executing Launch")
        await self.countdown()
        self.desired_altitude = fp["altitude"]
        flag1 = True
        flag2 = True
        flag3 = True
        flag4 = True
        while True:
            await asyncio.sleep(1)
            altitude = self.attr["altitude"]()
            apoapsis = self.attr["apoapsis"]()
            if altitude < self.turn_start_altitude:
                self.ap.target_pitch_and_heading(90,self.desired_heading)
            elif self.turn_start_altitude <= altitude < self.turn_mid_altitude:
                if flag1 == True:
                    self.mensseger.msg("Start ascending!")
                    flag1 = False
                #Only shallow out once we've got through the thicker part of the atmosphere.
                frac = self._proportion(altitude,self.turn_start_altitude,self.turn_mid_altitude)
                self.ap.target_pitch_and_heading(45 + 45*(1-frac),self.desired_heading)
            elif self.turn_mid_altitude <= altitude < self.turn_end_altitude:
                if flag2 == True:
                    self.mensseger.msg("Turn to middle altitude!")
                    flag2 = False
                frac = self._proportion(altitude, self.turn_mid_altitude, self.turn_end_altitude)
                self.ap.target_pitch_and_heading(35*(1-frac)+5 ,self.desired_heading)
            else:
                self.ap.target_pitch_and_heading(5, self.desired_heading)

            if altitude > self.vessel.orbit.body.atmosphere_depth:
                if flag4 == True:
                    self.mensseger.msg("Atmosphere Dept!")
                    flag4 = False
                fudge_factor = 1.0
            else:
                #Try and overshoot the desired altitude a little to account for resistence in the atmosphere
                fudge_factor = 1 + (self.vessel.orbit.body.atmosphere_depth - altitude) / (25 * self.vessel.orbit.body.atmosphere_depth)
            if apoapsis > self.desired_altitude * fudge_factor:
                if flag3 == True:
                    self.mensseger.msg("Throttle Off!")
                    flag3 = False
                self.vessel.control.throttle = 0
                if altitude > self.vessel.orbit.body.atmosphere_depth * 0.90:
                    # Wait until we're mostly out of the atmosphere before setting maneuver nodes
                    if flag3 == True:
                        self.mensseger.msg("Turn middle altitude!")
                        flag3 = False
                    self.ap.disengage()
                    return
            self.get_telemetry()
    
    async def countdown(self):
        # Start the sequence
        # await self.run_sequence()
        for i in range (5, 0, -1):
            self.mensseger.msg(f"{i} ...")
            await asyncio.sleep(1)

        self.vessel.control.activate_next_stage()

    async def run_sequence(self):
            self.loop.create_task(self._start_sequence())

            # ut = self.attr["ut"]()
            # self.loop.create_task(self.warp_to(ut + self.vessel.orbit.time_to_periapsis))
            # # The warp should stop in the atmosphere.
            # while True:
            #     altitude = self.attr["altitude"]()
            #     if altitude < self.vessel.orbit.body.atmosphere_depth * 0.90:
            #         break
            # #disable warping
            # self.drop_warp()
            # self.mensseger.msg("Turning")
            # self.ap.target_direction = (0,-1,0)
            # await asyncio.sleep(10) ## wait to turn.
            # self.mensseger.msg("Deceleration burn")
            # self.vessel.control.throttle = 1
            # await asyncio.sleep(20) ## Crude
            # self.vessel.control.throttle = 0
            # await asyncio.sleep(1) # Wait to check throttle is off before destaging
            # self.autostaging_disabled = True

            # chutes = False
            # while not chutes:
            #     stage = self.vessel.control.current_stage
            #     parts = self.vessel.parts.in_stage(stage-1)
            #     for part in parts:
            #         if part.parachute:
            #             chutes = True
            #     if chutes:
            #         self.mensseger.msg("Chutes in next stage.")
            #     else:
            #         self.mensseger.msg("Destaging for landing")
            #         self.vessel.control.activate_next_stage()

            # self.mensseger.msg("Deorbit Complete, brace for landing!!")
            # self.ap.disengage()

    async def autostager(self):
        while True:

            stage = self.vessel.control.current_stage
            parts = self.vessel.parts.in_stage(stage)
            for part in parts:
                if part.parachute:
                    self.msg("Chutes in stage. Disabling autostaging")
                    return

            parts = self.vessel.parts.in_decouple_stage(stage-1)
            fuel_in_stage = False
            for part in parts:
                engine = part.engine
                if engine and engine.active and engine.has_fuel:
                    fuel_in_stage = True


            if not fuel_in_stage:
                self.msg("No fuel in stage. Staging...")
                self.vessel.control.activate_next_stage()
            else:
                await asyncio.sleep(0.2)

class StageDeOrbit(Stages):
    def __init__(self,conn:Any,mensseger:Any, vessel:Any, ap:Any, fp:Any):
        self.conn=conn
        self.mensseger=mensseger
        self.vessel = vessel
        self.ap = ap
        self.fp = fp
        self.attr = {}
        self.attr["ut"] = KStream(conn, conn.space_center, 'ut')
        self.attr["periapsis"] = KStream(conn, vessel.orbit, 'periapsis_altitude')
        self.nav:Telemetry = TELEMETRY[Telemetries.NAV](self.conn)

    def get_telemetry(self):
        print(self.nav.get_telemetry())

    async def task(self, fp):
        self.mensseger.msg("Executing Deorbit")
        self.ap.reference_frame = self.vessel.orbital_reference_frame
        destage_altitude = self.vessel.orbit.body.atmosphere_depth * 0.90
        self.ap.target_direction = (0,-1,0)
        await asyncio.sleep(10) ## wait to turn.
        self.ap.engage()
        while True:
            cur_periapsis = self.attr["periapsis"]()
            self.ap.target_direction = (0,-1,0)
            if cur_periapsis > fp["periapsis"]:
                self.vessel.control.throttle = 0.5
            else:
                self.vessel.control.throttle = 0
                break

# need maneuver
class StageOrbit(Stages):
    def __init__(self,conn:Any, mensseger:Any, vessel:Any, ap:Any, fp:Any):
        self.conn=conn
        self.mensseger=mensseger
        self.vessel = vessel
        self.ap = ap
        self.fp = fp
        self.attr = {}
        self.attr["ut"] = KStream(conn, conn.space_center, 'ut')
        self.nav:Telemetry = TELEMETRY[Telemetries.NAV](self.conn)

    def get_telemetry(self):
        print(self.nav.get_telemetry())

    async def task(self, fp:dict):
        node = self.get_node()

        self.mensseger.msg(f"Changing Periapsis to new Apoapsis {fp['apoapsis']}")
        node.change_periapsis(fp["apoapsis"])
        asyncio.wait_for(node.execute(), None)

        self.mensseger.msg(f"Changing new Periapsis to {fp['periapsis']}")
        node.change_apoapsis(fp["periapsis"])
        asyncio.wait_for(node.execute(), None)

    def get_node(self):
        return ManeuverNode(self.conn, self.vessel, self.attr["ut"])


class StageLand(Stages):
    def __init__(self,conn:Any, mensseger:Any, vessel:Any, ap:Any, fp:Any):
        self.conn=conn
        self.mensseger=mensseger
        self.vessel = vessel
        self.ap = ap
        self.fp = fp
        self.attr = {}
        self.attr["altitude"] = KStream(conn, vessel.flight(), 'mean_altitude')
        self.nav:Telemetry = TELEMETRY[Telemetries.NAV](self.conn)

    def get_telemetry(self):
        print(self.nav.get_telemetry())
    async def task(self, fp:dict):
        self.mensseger.msg("Executing Landing")
        self.ap.reference_frame = self.vessel.orbital_reference_frame
        self.ap.target_direction = (0,-1,0)
        self.ap.engage()
        while True:
            altitude = self.attr["altitude"]()
            self.ap.target_direction = (0,-1,0)
            if altitude < fp["chute_altitude"]:
                while True:
                    stage = self.vessel.control.current_stage
                    parts = self.vessel.parts.in_stage(stage-1)
                    self.vessel.control.activate_next_stage()
                    for part in parts:
                        if part.parachute:
                            self.mensseger.msg("Chute stage activated")
                            return

class StageDiscard(Stages):
    async def task():
        pass

STAGES = {
    Stage.PRE_LAUNCH : StagePreLaunch,
    Stage.LAUNCH : StageLaunch,
    Stage.ORBIT: StageOrbit,
    Stage.DEORBIT : StageDeOrbit,
    Stage.LAND : StageLand,
    Stage.DISCARD: StageDiscard,
}

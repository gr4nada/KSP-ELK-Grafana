import sys
sys.path.append(".")

import asyncio
import threading
from typing import Any, Awaitable

from attr import attr
from ksp.Misc.Stages import STAGES, Stage
from ksp.FlightPlan import Situation, FlightContext


# class RunnerTasks():
#     def __init__(self,maxsize: int = 0) -> None:
#         self.queue = asyncio.Queue(maxsize)

#     async def add(self, name, *args, **kwargs):
#         self.draw.msg(f"Appending sequence: {name}")
#         await self.queue.put((name, self.seq_defs[name], args,kwargs))

#     async def get(self):
#         return self.queue.get()
#     async def get_tasks(self):
#         return self.queue

# class PipelineManager():
#     def __init__(self) -> None:
#         self.loop = asyncio.get_event_loop()
#         self.task = RunnerTasks(0)

#     async def execute(self):
#         while (self.task.queue.empty() == False):
#             try:
#                 self.loop.run_until_complete(self.task.get().task())
#             finally:
#                 self.loop.close()

class Controller(object):
    """_summary_

    Args:
        maxsize (int): number of items allowed in the queue. If maxsize <= 0 the queue size is infinite(Default).
    """
    def __init__(self, conn, maxsize: int = 0):
        self.conn = conn
        self.sc = self.conn.space_center
        self.av = self.sc.active_vessel
        # Kerbal Space Center
        self.ksc = self.conn.space_center
        # Build Status Dict to create a context Menu
        self.STATUS:dict ={
            self.ksc.VesselSituation.pre_launch:Situation.PRE_LAUNCH,
            self.ksc.VesselSituation.flying:Situation.FLYING,
            self.ksc.VesselSituation.escaping:Situation.ESCAPING,
            self.ksc.VesselSituation.orbiting:Situation.ORBITING,
            self.ksc.VesselSituation.docked:Situation.DOCKED,
            self.ksc.VesselSituation.sub_orbital:Situation.SUB_ORBITAL,
            self.ksc.VesselSituation.landed:Situation.LANDED,
            self.ksc.VesselSituation.splashed:Situation.SPLASHED,
        }
        # self.runner = RunnerTasks(maxsize)


    async def main(self, stage):
        """Schedule three calls *concurrently*:

        Args:
            stage (_type_): _description_
        """
        await asyncio.gather(
            stage,
        )

    def run(self, stage, flight_plan):
        # asyncio.run(stage.task(flight_plan))
        asyncio.run(self.main(stage.task(flight_plan)))
        
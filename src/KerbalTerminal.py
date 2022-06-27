from logging import exception
from typing import Protocol
import krpc
import os

from enum import Enum
from typing import Protocol

from ksp.Controller import Controller
from ksp.FlightPlan import Situation, FlightContext, Context
from ksp.Misc.Errors import AssumptionViolation,ConnectionError
from ksp.Misc.DataClasses import FlightPlan

class TypeInterface(Enum):
    CONSOLE = "console"
    KIVY = "kyvy"
    PYQT = "pyqt"
    FLASK = "flask"
    # ...


class UserInterface(Protocol):

    def update_context(context)->Context:
        ...

    def display():
        ...

    def get_action():
        ...


class Console(UserInterface):
    def __init__(self):
        self.logo()
        self.context:Context

    def update_context(self, context):
       self.context = context

    def display(self):
        for key, value in enumerate(self.context.display_actions()):
            print(f"        {key}-{value}")

    def get_action(self):
        choice = input("""
        Enter an option: """)
        return choice

    def logo(self):
        print("""
         _  __ _____ _____             __  __                  
        | |/ // ____|  __ \           |  \/  |                 
        | ' /| (___ | |__) |  ______  | \  / | ___ _ __  _   _ 
        |  <  \___ \|  ___/  |______| | |\/| |/ _ \ '_ \| | | |
        | . \ ____) | |               | |  | |  __/ | | | |_| |
        |_|\_\_____/|_|               |_|  |_|\___|_| |_|\__,_|
        """)

# class KivyTerminal(UserInterface):
#     ...
# class PyQTTerminal(UserInterface):
#     ...
# class FlaskTerminal(UserInterface):
#     ...
# ...


TERMINAL = {
    TypeInterface.CONSOLE: Console(),
    # TypeInterface.KIVY: KivyTerminal,
    # TypeInterface.PYQT: PyQTTerminal,
    # TypeInterface.FLASK: FlaskTerminal,
    # ...
}


class Messager(object):
    """ Draw text in the scene(feedbacks on game). """

    def __init__(self, conn) -> None:
        self.conn = conn

    def msg(self, msg, duration=5):
        self.conn.ui.message(msg, duration=duration)


class KerbalTerminal(object):
    """ A context menu to interate with a vessel in KSP game.
    """

    def __init__(self, terminal):
        # Set a terminal type
        self.term:UserInterface = terminal
        # Connect to Kerbal Space Center
        try:
            self.conn = krpc.connect(
                name=f"{os.path.basename(__file__)}.{os.getpid()}")
        except ConnectionError as error:
            print(f"Assumption was violated: {error.msg}")
            
        # Create a messeger to display text in the scene(feedbacks on Kerbal interface).
        self.messager = Messager(self.conn)
        # Load Vessel
        self.vessel = self.conn.space_center.active_vessel
        # Set the Auto_pilot
        self.ap = self.vessel.auto_pilot
        # TODO:create a Flight Plan
        self.fp = vars(FlightPlan())
        # TODO: create a Telemetry system

        # create a Controller
        self.control = Controller(self.conn)
        # Flight context initialization
        self.fc = FlightContext(self.conn, self.messager, self.vessel, self.ap, self.fp)
        # Context initialization
        self.context: Context = self.fc.FLIGHT[Situation.PRE_LAUNCH]
        # Update Context
        self.update_context()
        self.main_loop()

    def main_loop(self):
        '''Display the menu and respond to choices.'''
        while True:
            # Send a context to UI.
            self.update_context()
            # Display context information.
            self.term.display()
            # Get the user choice.
            choice = self.term.get_action()
            self.execute(choice)

    def execute(self, choice):
        # Exit Mode
        if choice == "0":
            self.close()
            exit(0)

        # Get a event.
        action = self.context.get_action(choice)
        if action:
            # Executes the action and performs the update.
            self.control.run(action, self.fp)

    def update_context(self) -> None:
        """Apply the terminal context from a vessel.situatuion.
        """
        try:
            self.context = self.get_context()
            self.term.update_context(self.context)

        except AssumptionViolation as error:
            print(f"Assumption was violated: {error.msg}")

    def get_context(self) -> Context:
        return self.fc.FLIGHT[self.get_status(self.vessel.situation)]

    def get_status(self, situation) -> Situation:
        """Get a vessel situation
        """
        return self.control.STATUS[situation]

    def close(self):
        self.conn.close()


def main():
    KerbalTerminal(TERMINAL[TypeInterface.CONSOLE])


if __name__ == '__main__':
    main()

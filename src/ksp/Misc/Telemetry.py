
import math

from enum import Enum
from typing import List, Protocol
from ksp.Misc.DataClasses import Part, Resource, Nav

class KStream(object):
    def __init__(self, conn, item, attr):
        self.stream = conn.add_stream(getattr, item, attr)

    def __call__(self):
        return self.stream()

class Telemetries(Enum):
    PART = "part"
    RESOURCE = "resource"
    NAV = "navegation"

class Telemetry(Protocol):
    def __init__(conn):
        ...

    def get_telemetry(self):
        ...

class PartTelemetry(Telemetry):
    def __init__(self,conn):
        self.conn = conn
        self.sc = self.conn.space_center
        self.av = self.sc.active_vessel
        self.avp = self.av.parts.all
        self.parts: List[Part] = []

    def get_telemetry(self) -> List[Part]:
        for p in self.avp:
            self.parts.append(Part(
                self.conn.add_stream(getattr, p, 'name')(),
                self.conn.add_stream(getattr, p, 'axially_attached')(),
                self.conn.add_stream(getattr, p, 'radially_attached')(),
                self.conn.add_stream(getattr, p, 'stage')(),
                self.conn.add_stream(getattr, p, 'decouple_stage')(),
                self.conn.add_stream(getattr, p, 'mass')(),
                self.conn.add_stream(getattr, p, 'dry_mass')(),
                self.conn.add_stream(getattr, p, 'dynamic_pressure')(),
                self.conn.add_stream(getattr, p, 'temperature')(),
                self.conn.add_stream(getattr, p, 'skin_temperature')(),
                self.conn.add_stream(getattr, p, 'thermal_conduction_flux')(),
                self.conn.add_stream(getattr, p, 'thermal_convection_flux')(),
                self.conn.add_stream(getattr, p, 'thermal_radiation_flux')(),
                self.conn.add_stream(getattr, p, 'thermal_internal_flux')()
            ))
        return self.parts

    def __call__(self):
        return self.parts

class ResourceTelemetry(Telemetry):

    def __init__(self,conn):
        self.conn = conn
        self.sc = self.conn.space_center
        self.av = self.sc.active_vessel
        self.avr = self.av.resources.all
        self.avp = self.av.parts.all
        self.parts: List[Part] = []
        self.resources: List[Resource] = []

    def get_telemetry(self) -> List[Resource]:
        for r in self.avr:
            self.resources.append(Resource(
                self.conn.add_stream(getattr, r, 'name')(),
                self.conn.add_stream(getattr, r, 'amount')(),
                self.conn.add_stream(getattr, r, 'max')(),
                self.conn.add_stream(getattr, r, 'density')()
            ))
        return self.resources

class NavTelemetry(Telemetry):
    def __init__(self,conn):
        self.conn = conn
        self.sc = self.conn.space_center
        self.av = self.sc.active_vessel
        self.avo = self.av.orbit
        self.avp = self.av.parts.all
        self.avf = self.av.flight()

    def get_telemetry(self) -> Nav:
        return vars(Nav(
            self.conn.add_stream(getattr, self.avo, 'apoapsis_altitude')(),
            self.conn.add_stream(getattr, self.avo, 'periapsis_altitude')(),
            self.conn.add_stream(getattr, self.avf, 'mean_altitude')(),
            self.conn.add_stream(getattr, self.avf, 'g_force')(),
            self.conn.add_stream(getattr, self.avf, 'rotation')(),
            self.conn.add_stream(getattr, self.avf, 'direction')(),
            self.conn.add_stream(getattr, self.avf, 'normal')(),
            self.conn.add_stream(getattr, self.avf, 'anti_normal')(),
            self.conn.add_stream(getattr, self.avf, 'radial')(),
            self.conn.add_stream(getattr, self.avf, 'anti_radial')(),
            self.conn.add_stream(getattr, self.avf, 'atmosphere_density')(),
            self.conn.add_stream(getattr, self.avf, 'dynamic_pressure')(),
            self.conn.add_stream(getattr, self.avf, 'static_pressure')(),
            self.conn.add_stream(getattr, self.avf, 'aerodynamic_force')(),
            self.conn.add_stream(getattr, self.avf, 'drag')(),
            self.conn.add_stream(getattr, self.avf, 'lift')(),
            self.conn.add_stream(getattr, self.sc, 'ut')(),
        ))

TELEMETRY = {
    Telemetries.NAV : NavTelemetry,
    Telemetries.PART : PartTelemetry,
    Telemetries.RESOURCE: ResourceTelemetry,
}

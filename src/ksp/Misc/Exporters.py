from typing import Protocol
from enum import Enum
from pylogbeat import PyLogBeatClient
#from kafka import KafkaProducer
import time
import os

# Config ELK
DEFAULT_ELK_ADDRESS = '127.0.0.1'
DEFAULT_ELK_PORT = 5959

# Config KAFKA
DEFAULT_KAFKA_ADDRESS = '127.0.0.1'
DEFAULT_KAFKA_PORT = 1234

class ExpoterMethod(Enum):
    CONSOLE = "console"
    FILE = "datafile"
    ELK = "elk"
    KAFKA = "kafka"

class Exporters(Protocol):
    def send():
        ...
    
    def close():
        ...

class ConsoleOutPut():
    """ Print Telemetry
    """
    def __init__(self) -> None:
        pass

    def send(self, json: dict ):
        print(json.dumps(json))
    
    def close():
        pass

class FileOutPut(object):
    """ Create a Log file
    """
    def __init__(self,id: str = "default"):
        self.uid = time.time()
        self.id=id

    def send(self,json: dict):
        log_file = f'{self.uid}_{id}.log'
        full_log_path = os.path.join(log_file)
        with open(full_log_path, "a") as file:
            file.write(json.dumps(json))
            file.write("\n")

    def close():
        pass

class ELKOutPut():
    """Send telemetry to Elastisearch
    """
    def __init__(self, host=DEFAULT_ELK_ADDRESS, port=DEFAULT_ELK_PORT):
        self.client = PyLogBeatClient( host, port, ssl_enable=False)
        self.client.connect()

    def send(self, telemetry):
        self.client.send([telemetry])

    def close(self):
        self.client.close()

class KafkaOutput():
    """Send telemetry to Apache Kafka
    """
    # TODO: IN Dev
    def __init__(self, bootstrap_servers=f'{DEFAULT_KAFKA_ADDRESS}:{DEFAULT_KAFKA_PORT}'):
        pass
       # self.producer = KafkaProducer(bootstrap_servers)

    def send(self, telemetry):
        # self.producer.send([telemetry])
        pass

    def close():
        pass


EXPORT = dict [ExpoterMethod, type[Exporters]]={
    ExpoterMethod.FILE : FileOutPut,
    ExpoterMethod.ELK : ELKOutPut,
    ExpoterMethod.KAFKA : KafkaOutput,
    ExpoterMethod.CONSOLE: ConsoleOutPut,
}
from btserver import BTServer
from btserver import BTError
from sensor import SensorServer

import argparse
import asyncore
import json
from random import uniform
from threading import Thread
from time import sleep, time

if __name__ == '__main__':
    # Create option parser
    usage = "usage: %prog [options] arg"
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", dest="output_format", default="csv", help="set output format: csv, json")
    parser.add_argument("--database", dest="database_name", default="air_pollution_data.db",
                        help="specify database file")

    args = parser.parse_args()

    # Create a BT server
    uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
    service_name = "GossipBTServer"
    server = BTServer(uuid, service_name)

    # Create the server thread and run it
    server_thread = Thread(target=asyncore.loop, name="Gossip BT Server Thread")
    server_thread.daemon = True
    server_thread.start()

    sensor_server = SensorServer(database_name=args.database_name)
    sensor_server.daemon = True
    sensor_server.start()

    while True:
        for client_handler in server.active_client_handlers.copy():
            # Use a copy() to get the copy of the set, avoiding 'set change size during iteration' error
            # Create CSV message "'realtime', time, temp, SN1, SN2, SN3, SN4, PM25\n"

            msg = ""
            sensor_output = sensor_server.get_sensor_output()

            realtime =int(time())
            temp = sensor_output.get('temp', -1)
            CO = sensor_output.get('CO', -1)
            NO2 = sensor_output.get('NO2', -1)
            SO2 = sensor_output.get('SO2', -1)
            O3 = sensor_output.get('O3', -1)
            PM25 = sensor_output.get('PM25', -1)

            msg = ""
            if args.output_format == "csv":
                        msg = "%f, %f, %f, %f, %f, %f" % (temp, CO, NO2, SO2, O3, PM25)
            elif args.output_format == "json":
                output = {  'realtime': realtime,
                            'O3': round(O3,1),
                            'NO2': round(NO2,1),
                            'PM25': round(PM25,1),
                            'CO': round(CO,1),
                            'SO2': round(SO2,1),
                            'temp': round(temp,1),
                          }
                msg = json.dumps(output)
            try:
                client_handler.send(msg + '\n')
            except Exception as e:
                BTError.print_error(handler=client_handler, error=BTError.ERR_WRITE, error_message=repr(e))
                client_handler.handle_close()

            # Sleep for 3 seconds
        sleep(3)

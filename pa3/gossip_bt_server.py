from btserver import BTServer
from bterror import BTError

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

    args = parser.parse_args()

    # Create a BT server
    uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
    service_name = "GossipBTServer"
    server = BTServer(uuid, service_name)

    # Create the server thread and run it
    server_thread = Thread(target=asyncore.loop, name="Gossip BT Server Thread")
    server_thread.daemon = True
    server_thread.start()

    while True:
        for client_handler in server.active_client_handlers.copy():
            # Use a copy() to get the copy of the set, avoiding 'set change size during iteration' error
            # Create CSV message "'realtime', time, temp, SN1, SN2, SN3, SN4, PM25\n"
            realtime = int(time())
            temp = uniform(20, 30)      # random temperature
            CO = uniform(0, 50.4)       # random SN1 value
            NO2 = uniform(0, 2049)       # random SN2 value
            SO2 = uniform(0, 1004)       # random SN3 value
            O3 = uniform(125, 604)     # random SN4 value
            PM25 = uniform(0, 500.4)    # random PM25 value

            msg = ""
            if args.output_format == "csv":
                        msg = "%f, %f, %f, %f, %f, %f" % (temp, CO, NO2, SO2, O3, PM25)
            elif args.output_format == "json":
                output = {
                            'name':'teamB_sensor',
                          'time': realtime,
                          'O3': round(O3,2),
                          'NO2': round(NO2,2),
                          'PM25': round(PM25,2),
                          'CO': round(CO,2),
                          'SO2': round(SO2,2),
                          'temp': round(temp,2),
                          }
                msg = json.dumps(output)
            try:
                client_handler.send(msg + '\n')
            except Exception as e:
                BTError.print_error(handler=client_handler, error=BTError.ERR_WRITE, error_message=repr(e))
                client_handler.handle_close()

            # Sleep for 3 seconds
        sleep(3)

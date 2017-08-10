import asyncore
import logging
import re
import sqlite3
from bterror import BTError

logger = logging.getLogger(__name__)

last_received_time = 0
first_received_time = 0
firstresults = 0
lastresults = 0
testfirsttime = 0
testlasttime = 0

class BTClientHandler(asyncore.dispatcher_with_send):
    """BT handler for client-side socket"""

    def __init__(self, socket, server):
        asyncore.dispatcher_with_send.__init__(self, socket)
        self.server = server
        self.data = ""
        self.sending_status = {'real-time': False, 'history': [False, -1, -1]}

    def selectfirsttime(self):
        try:
            # Create the database file and get the connection object.
            self.db_conn = sqlite3.connect(self.database_name)
            # Get database cursor from the connection object.
            self.db_cur = self.db_conn.cursor()
        except Exception as e:
            logger.error("Error connecting the database {}, reason: {}".format(self.database_name, e.message))
            self.__del__()

        if self.db_cur is None:
            print "ERROR"
        else:
            # If start time is smaller than or equal to end time AND SQL database is available, do SQL query
            # from the database.
            self.db_cur.execute("SELECT * FROM history WHERE time == {}".format(testfirsttime))
            # Get the result
            global results
            results = self.db_cur.fetchall()

    def handle_read(self):
        try:
            data = self.recv(1024)
            if not data:
                return

            lf_char_index = data.find('\n')

            if lf_char_index == -1:
                # No new line character in data, so we append all.
                self.data += data
            else:
                # We see a new line character in data, so append rest and handle.
                self.data += data[:lf_char_index]
                print "Received [{}]".format(self.data)

                self.handle_command(self.data)

                # Clear the buffer
                self.data = ""
        except Exception as e:
            BTError.print_error(handler=self, error=BTError.ERR_READ, error_message=repr(e))
            self.data = ""
            self.handle_close()


    def handle_command(self, command):
        # We should support following commands:
        # - start
        #       Start sending real time data by setting 'sending_status' variable to 0
        # - stop
        #       Stop sending real time data by setting 'sending_status' variable to False
        # - history start_time end_time
        #       Stop sending real time data, and query the history data from the database. Getting history data might
        #       take some time so we should use a different thread to handle this request
        if re.match('stop', command) is not None:
            global last_received_time
            # last_received_time = sqlite3.time()
            self.sending_status['real-time'] = False

            pass

        if re.match('start', command) is not None:
            if last_received_time is not 0:
                global testlasttime
                testlasttime = sqlite3.time()
                self.selectlasttime()
                global first_received_time
                first_received_time = lastresults
                self.sending_status['history'] = [True, int(last_received_time), int(first_received_time)]
            self.sending_status['real-time'] = True
            pass

        result = re.match(r"history (\d+) (\d+)", command)
        if result is not None:
            self.sending_status['history'] = [True, int(result.group(1)), int(result.group(2))]

    def handle_close(self):
        # flush the buffer
        while self.writable():
            self.handle_write()

        self.server.active_client_handlers.remove(self)
        self.close()

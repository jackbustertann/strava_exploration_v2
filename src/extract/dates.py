from datetime import datetime
from pytz import utc
from src.utils.gcp import GoogleBigQuery as gbq

class Dates():

    def get_current_date(self):

        self.current_datetime = datetime.now(tz = utc)
        self.current_date_str = datetime.strftime(self.current_datetime, '%Y-%m-%d')
        self.current_datetime_str = datetime.strftime(self.current_datetime, '%Y-%m-%dT%H:%M:%SZ')

    def get_run_date(self, gbq, use_run_date, run_date_str, gbq_table_id):

        if use_run_date:


            self.run_datetime = datetime.strptime(run_date_str, '%Y-%m-%d')
            self.run_date_str = run_date_str
            self.run_date_unix = int(self.run_datetime.timestamp())

            print(f'Running script using run date: {self.run_date_str} \n')

        else:

            self.run_datetime = gbq.get_latest_date(gbq_table_id, "start_date")
            self.run_date_str = datetime.strftime(self.run_datetime, '%Y-%m-%d')
            self.run_date_unix = int(self.run_datetime.timestamp())

            print(f'Running script using run date: {self.run_date_str} \n')


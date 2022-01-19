# Imports
import requests

# Constant
ENDPOINT = "http://127.0.0.1:5000/show-logs/"


class ApiTest:

    def __init__(self, limit, scrolling, timestamp='0000-00-00 00:00:00.000', user_id='NOT_EXISTING_USER_ID'):
        self.timestamp = timestamp
        self.user_id = user_id
        self.limit = limit
        self.scrolling = scrolling
        self.params = {
            "anchor_timestamp": self.timestamp,
            "user_id": self.user_id,
            "log_appearance_limit": self.limit,
            "scrolling": self.scrolling
        }

    def hit_api(self):
        """Request the api with the object params"""
        res = requests.get(ENDPOINT, params=self.params)
        return res

    def valid_status_code(self, res):
        """Return True for 200 HTTP return code"""
        return int(res.status_code) == 200

    def valid_number_of_logs_by_limit(self, res):
        """count the number of logs by keyword. Return True if it's twice limit logs number + 1 (anchor)"""

        returned_data = res.text
        number_of_logs = returned_data.count("timestamp")
        return number_of_logs == ((2 * self.limit) + 1)

    def is_anchor_at_the_center(self, res):
        """loop over the logs that return from res, find the anchor index.
         Return True if the anchor is centered"""

        logs = res.json()['logs']
        counter = 0
        for log in logs:
            if log['timestamp'] != self.timestamp:
                counter += 1
            else:
                return len(logs[counter::]) == len(logs[counter::-1])

    def valid_scrolling_check(self, direction):
        """
        first: for gets data about the logs dataset,
        secondly: to show the possibility of scrolling to forward/backward
        logs and thirdly: to show the correct limitation of the log_appearance_limit (raise 400 return code).

        :param direction: 'backward' to move to newest logs and forward for the opposite.
        :return: boolean
        """

        self.params["scrolling"] = 0  # reset anchor state
        sampling_res = self.hit_api()
        scrolling_to_end = sampling_res.json()['scrolling_steps_to_end']
        scrolling_to_start = sampling_res.json()['scrolling_steps_to_start']

        if direction == "forward":
            scroll_before_error = scrolling_to_end - self.limit
            scroll_after_error = scrolling_to_end - self.limit + 1

        elif direction == "backward":
            scroll_before_error = -1 * (scrolling_to_start - self.limit)
            scroll_after_error = -1 * (scrolling_to_start - self.limit + 1)

        else:
            return "wrong input"

        # check the valid limit return value
        self.params["scrolling"] = scroll_before_error
        res = self.hit_api()
        before_status_code = res.status_code

        # check the invalid limit return value
        self.params["scrolling"] = scroll_after_error
        res = self.hit_api()
        after_status_code = res.status_code

        # True if scrolling can be made with correctly limitation.
        return before_status_code == 200 and after_status_code == 400

    def is_user_id_valid(self):
        """Request the api with invalid user_id. Return True for 400 HTTP return code"""

        self.params["user_id"] = "................."
        res = self.hit_api()
        return res.status_code == 400

    def is_timestamp_valid(self):
        """Request the api with invalid timestamp. Return True for 400 HTTP return code"""

        self.params['anchor_timestamp'] = '0000-00-00 00:00:00.000'
        res = self.hit_api()
        return res.status_code == 400

    def valid_log_appearance_limit(self):
        """Request the api with invalid log_appearance_limit. Return True for 400 HTTP return code"""

        self.params['log_appearance_limit'] = -1
        res = self.hit_api()
        return res.status_code == 400


def main():
    # All the params are correct, valid number of logs, anchor at the center.     
    test = ApiTest(limit=1,
                   scrolling=0,
                   timestamp="2021-01-09 23:01:59.140",
                   user_id="31b20726-b870-47ba-bbcd-372b38527c89")

    res = test.hit_api()
    print(f"valid status code: {test.valid_status_code(res)}")
    print(f"valid number of logs: {test.valid_number_of_logs_by_limit(res)}")
    print(f"valid center anchor: {test.is_anchor_at_the_center(res)}")
    print(f"valid forward scrolling limitation: {test.valid_scrolling_check('forward')}")
    print(f"valid backward scrolling limitation: {test.valid_scrolling_check('backward')}")
    test.params['scrolling'] = 0
    print(f"valid api error response to invalid user_id: {test.is_user_id_valid()}")
    test.params['user_id'] = "31b20726-b870-47ba-bbcd-372b38527c89"
    print(f"valid api error response to invalid timestamp: {test.is_timestamp_valid()}")
    test.params['anchor_timestamp'] = "2021-01-09 23:01:59.140"
    print(f"valid api error response to invalid log_appearance_limit: {test.valid_log_appearance_limit()}")


if __name__ == '__main__':
    main()
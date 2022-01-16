import json
import logging
import random
import requests
import sys
import time
import urllib3
import yaml
from itertools import product

logger = logging.getLogger("sampler.runrequests")

class Requester:
    def __init__(self, app: str, n1: int, n2: int):
        self._app = app
        self._n1 = n1
        self._n2 = n2
        self._unfetched_traces = []
        self._cfg = yaml.full_load(open("./config.yaml"))
        self._slscfg = yaml.full_load(open(f"../apps/{self._app}/serverless.yaml"))
        self._patience = 6
        urllib3.disable_warnings()

    def _sample_missing_function_anomalies(self, numb_missing_function_anomalies: int) -> list[str]:
        if numb_missing_function_anomalies == 0:
            return []
        func_names = list(self._slscfg["functions"])
        func_names.remove("main")
        if numb_missing_function_anomalies > len(func_names):
            logger.error(f"Flag -m is too large. Maximum value is {len(func_names)}.")
        return random.sample(func_names, numb_missing_function_anomalies)
    
    def _sample_execution_anomalies(self, numb_execution_anomalies: int, missing_function_anomalies: list[str]) -> list[str]:
        if numb_execution_anomalies == 0:
            return []
        func_names = set(self._slscfg["functions"]) - set(missing_function_anomalies)
        func_names.remove("main")
        if numb_execution_anomalies > len(func_names):
            logger.error(f"Flag -e is too large. Maximum value is {len(func_names)}.")
        return random.sample(func_names, numb_execution_anomalies)
    
    def _fetch_zipkin(self, params: dict) -> list:
        APIHOST = f"http://{self._cfg['zipkin']['host']}"
        url = APIHOST + "/api/v2/traces"
        traces = []
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            traces = response.json()
        except Exception as e:
            logger.error(f"Unable to perform request to {url}. {e}")
        return traces

    def _trace_complete(self, trace, numb_missing_function_anomalies) -> bool:
            # Get the function names of the Serverless application.
            func_names = set(self._slscfg["functions"])
            if "conductor" in func_names:
                func_names.remove("conductor")
            # Check if each function name has a respective span in the trace.
            span_names = set(map(lambda span: span["name"], trace))
            f = lambda func_span_name: func_span_name[0] == func_span_name[1][-len(func_span_name[0]):]
            funcs_with_spans = list(filter(f, product(func_names, span_names)))
            if len(funcs_with_spans) == (len(func_names) - numb_missing_function_anomalies):
                return True
            return False

    def run_requests(
        self,
        first_lower_bound,
        first_upper_bound,
        second_lower_bound,
        second_upper_bound,
        numb_execution_anomalies,
        numb_missing_function_anomalies,
        random_execution_duration
    ) -> list:
        APIHOST = f"https://{self._cfg['openwhisk']['host']}"
        AUTH_KEY = self._cfg['openwhisk']['auth']
        NAMESPACE = "_"
        ACTION = f"{self._app}-dev-main"
        BLOCKING = "false"
        RESULT = "true"
        url = APIHOST + "/api/v1/namespaces/" + NAMESPACE + "/actions/" + ACTION
        user_pass = AUTH_KEY.split(":")
        headers = {"content-type": "application/json"}
        # The UNIX timestamp in milliseconds represents a unique and meaningful id.
        sample_id = int(time.time() * 1e3)

        count = 0
        while count < (self._n1 + self._n2):
            missing_function_anomalies = self._sample_missing_function_anomalies(numb_missing_function_anomalies)
            execution_anomalies = self._sample_execution_anomalies(numb_execution_anomalies, missing_function_anomalies)
            data = json.dumps({
                "sampleId": sample_id,
                "executionAnomalies": execution_anomalies,
                "missingFunctionAnomalies": missing_function_anomalies,
                "random": random_execution_duration
            })
            try:
                response = requests.post(
                                url, 
                                params={"blocking": BLOCKING, "result": RESULT}, 
                                data=data, 
                                auth=(user_pass[0], user_pass[1]),
                                verify=False, 
                                headers=headers
                           )
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                logger.error(f"Unable to perform request to {url}. {e}")
                time.sleep(30)
                continue
           
            count += 1
            logger.info(f"{count} of {self._n1 + self._n2} requests performed {response.text}.")
            
            dur = 0
            log_str = ""
            if count % 50 == 0:
                dur = 120
            else:
                dur = random.uniform(second_lower_bound, second_upper_bound)
                log_str = f" Lower-bound={second_lower_bound}, upper-bound={second_upper_bound}."    
            logger.info(f"Wait {round(dur, 2)} seconds until next request.{log_str}")
            time.sleep(dur)

            self._unfetched_traces.append(response.json()["activationId"])
        
        # Fetch complete traces from Zipkin one by one
        logger.info(f"Trying to fetch the traces from Zipkin ...")    
        traces = []
        impatient = 0
        while impatient <= self._patience:
            last_num_unfetched_traces = len(self._unfetched_traces)
            
            for aid in self._unfetched_traces.copy():
                trace = self._fetch_zipkin(params={"annotationQuery": f"activationId={aid}"})
                if len(trace) == 0:
                    continue
                if self._trace_complete(trace[0], numb_missing_function_anomalies):
                    traces.append(trace[0])
                    self._unfetched_traces.remove(aid)
            if last_num_unfetched_traces == len(self._unfetched_traces):
                impatient += 1
            if len(self._unfetched_traces) == 0:
                break
            logger.info(f"{len(self._unfetched_traces)} traces are not yet complete: {self._unfetched_traces[:4]} ... Retrying ...")
            time.sleep(60)
        else:
            logger.info("Termination as the number of unfetched traces stagnated after multiple retries.")
        logger.info(f"Fetched {len(traces)} traces from Zipkin.")
        return traces
from functools import total_ordering

@total_ordering
class Span:
    """
    A Span represents a function invocation.

    Args:
        name: Name of the function the span is representing
        start: Unix timestamp in milliseconds representing executionStart - waitTime - initTime
        duration: Time intervall in milliseconds representing executionTime + waitTime + initTime
        wait: OpenWhisk waitTime of function invocation in milliseconds
        init: OpenWhisk initTime of function invocation in milliseconds
    """
    def __init__(self, name: str, start: int, duration: int, wait: int, init: int):
        self.name = name
        self.start = start
        self.duration = duration
        self.wait = wait
        self.init = init

    def __eq__(self, other) -> bool: 
        return self.start == other.start

    def __lt__(self, other) -> bool:
        return self.start < other.start

class Trace:
    """
    A trace contains the ordered information of multiple Span objects.

    Args:
        spans: A list of Span objects
        mapping: A dictionary which maps the function names to integers
    """
    def __init__(self, spans: list[Span], mapping: dict[str, int]):
        self.arrival_times = []
        self.marks = []
        self.wait_times = []
        self.init_times = []
        spans.sort()
        for span in spans:
            self.arrival_times.append(span.start)
            self.marks.append(mapping[span.name])
            self.wait_times.append(span.wait)
            self.init_times.append(span.init)
        self.t_end = self.arrival_times[-1]

    def asdict(self) -> dict:
        return {
                "arrival_times": self.arrival_times, 
                "marks": self.marks, 
                "wait_times": self.wait_times, 
                "init_times": self.init_times,
                "t_end": self.t_end
               }

def create_dataset(ztraces: list, mapping: dict[str, int]) -> list[dict]:
    """
    Extracts the start, wait, and init time and the function name from the traces
    received from Zipkin.

    Args:
        ztraces: A list of traces received from the Zipkin /api/v2/traces endpoint
        mapping: A dictionary which maps the function names to integers
    
    Returns:
        traces: A list of dictionaries where each dictionary represents 
                the information of one trace.
                [
                    {
                        arrival_times: [1, 2, 5], marks: [1, 2, 4], 
                        wait_times: [20, 80, 10], init_times: [10, 0, 0], 
                        t_end: 5
                    }, 
                    {...}, 
                    ...
                ]
    """
    traces = []
    for ztrace in ztraces:
        spans = []
        for span in ztrace:
            tags = span["tags"]
            # If span represents a cold start, init time is omitted.
            if "initTimeMilli" in tags: 
                init = tags["initTimeMilli"]
            else: 
                init = 0
            # Spans received from Zipkin are in the time unit microseconds.
            ts_milli = span["timestamp"] / 1e3
            dur_milli = span["duration"] / 1e3
            if span["name"] in ["wait", "init", "exec"]: 
                continue
            name = span["name"][span["name"].rfind('/')+1:]
            s = Span(name=name, 
                     start=ts_milli, 
                     duration=dur_milli, 
                     wait=int(tags["waitTimeMilli"]), 
                     init=int(init))
            spans.append(s)
        traces.append(Trace(spans, mapping).asdict())
    return {
            "sequences": traces,
            "num_marks": len(mapping),
            "mapping": mapping
           }
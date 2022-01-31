from datetime import datetime
from sampler import Requester
from sampler import create_dataset
import argparse
import torch
import yaml

def _func_name_mapping(app: str) -> dict[str, int]:
    stream = open(f"../apps/{app}/serverless.yaml")
    cfg = yaml.full_load(stream)
    funcs = set(cfg["functions"])
    mapping = {}
    for i, func in enumerate(funcs):
        mapping[f"{app}-dev-{func}"] = i
    return mapping

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", type=str, help="App directory name")
    parser.add_argument("-n", default=0, type=int, help="Number of requests")
    parser.add_argument("-l", dest="lower_bound", type=float, help="Lower bound of inter-request duration")
    parser.add_argument("-u", dest="upper_bound", type=float, help="Upper bound of inter-request duration")
    parser.add_argument("-b", dest="batch_size", help="Size of request batch")
    parser.add_argument("-w", dest="pause_duration", help="Pause duration after each batch")
    parser.add_argument("-e", dest="numb_execution_anomalies", type=int)
    parser.add_argument("-m", dest="numb_missing_function_anomalies", type=int)
    parser.add_argument("-r", dest="random_execution_duration", type=int)
    args = parser.parse_args()

    if args.batch_size:
        args.batch_size = int(args.batch_size)
        args.pause_duration = int(args.pause_duration)

    req = Requester(args.d)
    traces = req.run_requests(
        args.n,
        args.lower_bound,
        args.upper_bound,
        args.batch_size,
        args.pause_duration,
        args.numb_execution_anomalies,
        args.numb_missing_function_anomalies,
        args.random_execution_duration
    )
    dataset = create_dataset(traces, mapping=_func_name_mapping(args.d))
    datetimestr = datetime.now().strftime("%Y%m%d_%H:%M")
    
    b_str = ""
    w_str = ""
    if args.batch_size:
        b_str = f"_b_{args.batch_size}"
        w_str = f"_w_{args.pause_duration}"
    rand_str = ""
    if args.random_execution_duration:
        rand_str = "_rand"
    e_ano_str = ""
    if args.numb_execution_anomalies > 0:
        e_ano_str = f"_e_{args.numb_execution_anomalies}"
    m_ano_str = ""
    if args.numb_missing_function_anomalies > 0:
        m_ano_str = f"_m_{args.numb_missing_function_anomalies}"
    with open(
        f"../data/{datetimestr}_{args.d}_fetched_{len(traces)}_n_{args.n}_l_{args.lower_bound}_u_{args.upper_bound}{b_str}{w_str}{rand_str}{e_ano_str}{m_ano_str}.pkl", "wb"
    ) as f:
        torch.save(dataset, f, pickle_protocol=4)
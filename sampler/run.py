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
    if "conductor" in funcs:
        funcs.remove("conductor")
    mapping = {}
    for i, func in enumerate(funcs):
        mapping[f"{app}-dev-{func}"] = i
    return mapping

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", type=str, help="App directory name")
    parser.add_argument("-n1", default=0, type=int, help="Number of requests")
    parser.add_argument("-l1", dest="first_lower_bound", type=float, help="Lower bound of inter-request duration")
    parser.add_argument("-u1", dest="first_upper_bound", type=float, help="Upper bound of inter-request duration")
    parser.add_argument("-n2", default=0, type=int, help="Number of requests")
    parser.add_argument("-l2", dest="second_lower_bound", type=float, help="Lower bound of inter-request duration")
    parser.add_argument("-u2", dest="second_upper_bound", type=float, help="Upper bound of inter-request duration")
    parser.add_argument("-e", dest="numb_execution_anomalies", type=int)
    parser.add_argument("-m", dest="numb_missing_function_anomalies", type=int)
    parser.add_argument("-r", dest="random_execution_duration", type=int)
    args = parser.parse_args()

    req = Requester(args.d, args.n1, args.n2)
    traces = req.run_requests(
        args.first_lower_bound,
        args.first_upper_bound,
        args.second_lower_bound,
        args.second_upper_bound,
        args.numb_execution_anomalies,
        args.numb_missing_function_anomalies,
        args.random_execution_duration
    )
    dataset = create_dataset(traces, mapping=_func_name_mapping(args.d))
    datetimestr = datetime.now().strftime("%Y%m%d_%H:%M")
    
    n2_str = ""
    l2_str = ""
    u2_str = ""
    if args.n2 > 0:
        n2_str = f"_n2_{args.n2}"
        l2_str = f"_l2_{args.second_lower_bound}"
        u2_str = f"_u2_{args.second_upper_bound}"
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
        f"../data/{datetimestr}_{args.d}_fetched_{len(traces)}_n1_{args.n1}_l1_{args.first_lower_bound}_u1_{args.first_upper_bound}{n2_str}{l2_str}{u2_str}{rand_str}{e_ano_str}{m_ano_str}.pkl", "wb"
    ) as f:
        torch.save(dataset, f, pickle_protocol=4)
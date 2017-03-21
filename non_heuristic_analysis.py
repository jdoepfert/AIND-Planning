import os

import pandas as pd
from timeit import default_timer as timer

from run_search import PROBLEMS, PrintableProblem
from aimacode.search import (breadth_first_search, astar_search,
    breadth_first_tree_search, depth_first_graph_search, uniform_cost_search,
    greedy_best_first_graph_search, depth_limited_search,
    recursive_best_first_search)
from my_air_cargo_problems import air_cargo_p1, air_cargo_p2, air_cargo_p3


PROBLEMS = [["Air Cargo Problem 1", air_cargo_p1],
            ["Air Cargo Problem 2", air_cargo_p2],
            ["Air Cargo Problem 3", air_cargo_p3]]
SEARCHES = [["breadth_first_search", breadth_first_search, ""],
            ['breadth_first_tree_search', breadth_first_tree_search, ""],
            ['depth_first_graph_search', depth_first_graph_search, ""],
            ['depth_limited_search', depth_limited_search, ""],
            ['uniform_cost_search', uniform_cost_search, ""],
            ['greedy_best_first_graph_search', greedy_best_first_graph_search, 'h_1'],
            ]
# exclude some searches since they take too long (>10min)
EXCLUDE_IDX = [(1, 1),   # breadth first tree on prob 2
               (2, 3),   # depth limited searchon prob 3
               (2, 1),]  # breadth first tree on prob 3


def run_search(problem, search_function, parameter=None):
    start = timer()
    ip = PrintableProblem(problem)
    if parameter is not None:
        node = search_function(ip, parameter)
    else:
        node = search_function(ip)
    end = timer()
    elapsed_time = end - start
    return ip, node, elapsed_time


def evaluation(ip, node, elapsed_time):
    return  {'Expansions':ip.succs,
             'Goal Tests':ip.goal_tests,
             'New Nodes': ip.states,
             'Plan Lenght': len(node.solution()),
             'Time': elapsed_time,
             'Actions': ["{}{}".format(action.name, action.args)
                         for action in node.solution()]
            }


def failed_evaluation():
     return {'Expansions': '-',
             'Goal Tests': '-',
             'New Nodes': '-',
             'Plan Lenght': '-',
             'Time': '-',
             'Actions': '-'
            }

 
def entry_already_stored(prob_idx, search_idx, filename, key='test'):
    pname, p = PROBLEMS[prob_idx]
    sname, s, h = SEARCHES[search_idx]
    df = pd.read_hdf(filename, key)
    where = (df['Problem'] == pname) & (df['Search Method'] == sname)
    return not df[where].empty

    
def create_report_df(prob_idx, search_idx):
    problem_name, p = PROBLEMS[prob_idx]
    search_name, s, h = SEARCHES[search_idx]
    hstring = h if not h else " with {}".format(h)
    
    if not (prob_idx, search_idx) in EXCLUDE_IDX:
        print("\nSolving {} using {}{}...".format(problem_name, search_name, hstring))

        _p = p()
        _h = None if not h else getattr(_p, h)
        results = run_search(_p, s, _h)

        report = evaluation(*results)
    else:
        print("\nSkipping {} using {}{}...".format(problem_name, search_name, hstring))
        report = failed_evaluation()

    report['Problem'] = problem_name
    report['Search Method'] = search_name
    return pd.DataFrame([report])


def store_append_df(df, filename='non_heuristic_report.h5', key='test'):    
    if isinstance(df, pd.DataFrame):
        if not os.path.isfile(filename):
            df.to_hdf(filename, key)
        else:
            df_old = pd.read_hdf(filename, key)
            df_new = df_old.append(df)
            df_new.to_hdf(filename, key)


def run_analysis(filename):
    for prob_idx in range(len(PROBLEMS)):
        for search_idx in range(len(SEARCHES)):
            if not entry_already_stored(prob_idx, search_idx, filename):                
                report = create_report_df(prob_idx, search_idx)
                store_append_df(report, filename)
                

if __name__ == '__main__':
    filename='data/non_heuristic_report.h5'
    run_analysis(filename)

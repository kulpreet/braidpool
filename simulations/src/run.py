import argparse
import logging
import random

import networkx as nx
import simpy

from config import config
from topology import Topology


def run(*, num_nodes, num_neighbours):
    run_time = int(config["simulation"]["run_time"])

    logging.basicConfig(
        format="%(message)s",
        level=config["logging"]["level"],
        filename=f"logs/{num_nodes}_{num_neighbours}_{run_time}.log",
        filemode='w'
    )

    logging.info("Process communication")
    random.seed(config["simulation"]["random_seed"])
    env = simpy.Environment()

    network = Topology(env=env, num_nodes=num_nodes, num_neighbours=num_neighbours)
    for node in network.nodes.values():
        node.start()

    logging.info("\nP2P broadcast communication\n")
    env.run(until=run_time)

    for node in network.nodes.values():
        logging.debug(list(nx.lexicographical_topological_sort(node.dag)))
        logging.debug(node.dag.edges())
        if config.getboolean("simulation", "save_dot"):
            g = nx.nx_agraph.to_agraph(node.dag)
            g.layout()
            g.draw(f"/tmp/node_{node.name}.png", prog="dot")
        if node.shares_sent:
            logging.info(
                f"node: {node.name} sent: {len(node.shares_sent)} ({node.num_blocks}), "
                f"not rewarded: {len(node.shares_not_rewarded)}"
                f" %age not rewarded {len(node.shares_not_rewarded)/len(node.shares_sent) * 100}"
            )
        else:
            logging.info(
                f"node: {node.name} sent: {len(node.shares_sent)} ({node.num_blocks}), "
                f"not rewarded: {len(node.shares_not_rewarded)}"
            )
        logging.info(node.shares_not_rewarded)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_nodes", "-n", type=int, help="Number of nodes")
    parser.add_argument(
        "--num_neighbours", "-d", type=int, help="Number of neighbors per node"
    )
    args = parser.parse_args()
    run(num_nodes=args.num_nodes, num_neighbours=args.num_neighbours)

'''yans
Yet Another Network Simulator

Usage:
  yans [-V] [-t --topo=<topo_path>] (up|stop|destroy)
  yans [-V] [-t --topo=<topo_path>] console <node_name> -c <commands>
  yans -h | --help
  yans --version

Options:
  -h --help                 Show this screen.
  --version                 Show version.
  -t --topo=<topo_path>     Network topology YAML [default: ./topo.yaml].
  -V --verbose              Verbose mode
'''

from __future__ import unicode_literals, print_function
import logging
import sys
from docopt import docopt

from docker_command import destroy_links, create_nodes, create_links, ensure_docker_machine, destroy_nodes, bind_interface, exec_in_node
from topology import Topology, TopologySpecError

__version__ = "0.1.0"
__author__ = "Kenneth Jiang"
__license__ = "MIT"


def main():
    '''Main entry point for the yans CLI.'''
    args = docopt(__doc__, version=__version__)

    ensure_docker_machine()

    if args['--verbose']:
        logging.getLogger().setLevel(logging.DEBUG)

    topo_file = args['--topo']
    try:
        topo = Topology(topo_file)
    except TopologySpecError as err:
        sys.exit(err)

    if args['up']:
        create_links(topo.links)
        create_nodes(topo.nodes)
        for link in topo.links:
            for interface in link.interfaces:
                bind_interface(interface)
        topo.draw()
        print('To run commands in each node:')
        for node in topo.nodes:
            print('`$ yans -t ' + topo_file + ' console ' + node.name +
                  ' -c <"Commands">`')

    if args['destroy']:
        destroy_nodes(topo.nodes)
        destroy_links(topo.links)

    if args['console']:
        node_name = args['<node_name>']
        commands = args['<commands>']
        node = topo.node_by_name(node_name)
        if node:
            exec_in_node(node, commands)
        else:
            sys.exit('Node named "' + node_name + '" is not found in ' +
                     topo_file)


if __name__ == '__main__':
    main()

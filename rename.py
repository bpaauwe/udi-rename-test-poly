#!/usr/bin/env python3
"""
Polyglot v3 node server rename test
Copyright (C) 2021 Robert Paauwe

MIT License
"""
import udi_interface
import sys
import time

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom
polyglot = None
new_name = 'default'
node_list = []

'''
TestNode is the device class.  Our simple counter device
holds two values, the count and the count multiplied by a user defined
multiplier. These get updated at every shortPoll interval
'''
class TestNode(udi_interface.Node):
    id = 'test'
    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2},
            {'driver': 'GV0', 'value': 0, 'uom': 56},
            {'driver': 'GV1', 'value': 0, 'uom': 56},
            ]

    def noop(self):
        LOGGER.info('Discover not implemented')

    commands = {'DISCOVER': noop}


'''
Read the user entered custom parameters. In this case, it is just
the 'multiplier' value.  Save the parameters in the global 'Parameters'
'''
def parameterHandler(params):
    global polyglot
    global new_name

    LOGGER.error('CUSTOMPARAMS handler called {}'.format(params))

    # if the node exists, try renaming it
    node = polyglot.getNode('addr_0001')
    if node:
        LOGGER.error('User is renaming node {} to {}'.format(node.name, params['name']))
        polyglot.renameNode(node.address, params['name'])

    LOGGER.error('Finished processing custom parameters')



def configHandler(data):
    global node_list
    LOGGER.error('CONFIGDONE handler called')
    if data:
        LOGGER.error('  -> nodes = {}'.format(data['nodes']))
        node_list = data['nodes']

if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start('1.0.0')

        # subscribe to the events we want
        polyglot.subscribe(polyglot.CUSTOMPARAMS, parameterHandler)
        polyglot.subscribe(polyglot.CONFIG, configHandler)

        # Start running
        polyglot.ready()
        polyglot.setCustomParamsDoc()
        polyglot.updateProfile()

        '''
        On start there should be no nodes in the node_internal list
        '''
        nodes = polyglot.getNodes()
        LOGGER.error('On start, found nodes: {}'.format(nodes))

        LOGGER.error('Nodes from config = {}'.format(node_list))
        for node in node_list:
            LOGGER.error('Found node: {}'.format(node))
            LOGGER.error('Found node: {}/{}'.format(node['name'],node['address']))
            # if we try to rename a node now it should fail!
            LOGGER.error('renaming node {} to {}'.format(node['name'], new_name))
            polyglot.renameNode(node['address'], new_name)

            # now what happens if we try to create a node using the new name
            node = TestNode(polyglot, node['address'], node['address'], new_name)
            polyglot.addNode(node, conn_status="ST")

        nodes = polyglot.getNodes()
        if len(nodes) == 0:
            LOGGER.error('No existing nodes, create one')
            node = TestNode(polyglot, 'addr_0001', 'addr_0001', 'OriginalName')
            polyglot.addNode(node, conn_status="ST")


        time.sleep(10)
        LOGGER.error('getNode = {}'.format(polyglot.getNode('addr_0001').name))

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        


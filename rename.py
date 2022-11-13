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

    new_name = params['name']

    LOGGER.error('Finished processing custom parameters')



def configHandler(data):
    LOGGER.error('CONFIGDONE handler called')
    if data:
        LOGGER.error('  -> nodes = {}'.format(data['nodes']))

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
        On first start there should be no node.  If there are no nodes
        then add a node.
        '''
        nodes = polyglot.getNodes()
        LOGGER.error('On start, found nodes: {}'.format(nodes))
        if (len(nodes) == 0):
            # add the node
            LOGGER.error('Creating node with name "OriginalName"')
            node = TestNode(polyglot, 'addr_0001', 'addr_0001', 'OriginalName')
            polyglot.addNode(node, conn_status="ST")

            # now rename the node
            LOGGER.error('renaming node to {}'.format(new_name))
            polyglot.rename('addr_0001', new_name)
        else:
            # rename the node to what was specified in the custom parameter
            LOGGER.error('renaming node to {}'.format(new_name))
            polyglot.rename('addr_0001', new_name)

            LOGGER.error('Creating node with name "{}"'.format(new_name))
            node = TestNode(polyglot, 'addr_0001', 'addr_0001', new_name)
            polyglot.addNode(node, conn_status="ST")

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        


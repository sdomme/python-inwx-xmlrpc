#!/usr/bin/env python
# -*- encoding: UTF8 -*-

import sys, os
sys.path.append(os.path.dirname(__file__))

from inwx import domrobot
from configuration import get_account_data, get_domain_update

config_file = os.path.dirname(__file__) + '/python-inwx-xmlrpc.cfg'

def update_dns(new_ip):
    record_types = ['A', 'AAAA']

    api_url, username, password = get_account_data(True, config_file)
    domain, subdomain, _ = get_domain_update(True, config_file)

    # Instantiate the inwx class (does not connect yet but dispatches calls to domrobot objects with the correct API URL
    inwx_conn = domrobot(api_url, username, password, 'en', False)
    nsentries = inwx_conn.nameserver.info({'domain': domain})

    # Filter entries for subdomain
    records = [record for record in nsentries['record'] if subdomain == record['name']]

    if not records:
	status = "404 Failed"
	return "Subdomain {0} not in list of nameserver entries".format(subdomain), status

    for record in records:
        record_type = record['type']
	if record_type not in record_types:
	    status = "404 Failed"
            return "Unsupported record type: {0}".format(record_type), status
        
	if new_ip != record['content']:
	    try:
	        inwx_conn.nameserver.updateRecord({'id': record['id'], 'content': new_ip, 'ttl': 3600})
    		status = "200 OK"
                return "Updating record {0} from {1} to {2}".format(record['name'], record['content'], new_ip), status
	    except Exception as e:
	        status = "404 Failed"
                return "Failed {0} record of {1} from {2} to {3}::::{4}".format(record_type, record['name'], record['content'], new_ip, e.message), status
	else:
	     status = "200 OK"
             return "Same IP", status

def application(environ, start_response):
    ip = environ['REMOTE_ADDR']
    response_body, status = update_dns(ip)
    response_headers = [('Content-type', 'text/plain'), ('Content-Length', str(len(response_body)))]
    start_response(status, response_headers)
    return [response_body]

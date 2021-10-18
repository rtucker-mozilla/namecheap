#!/usr/bin/env python3
import argparse
import sys
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlencode
from urllib.request import urlretrieve
from common import parse_errors, transaction_succeeded, get_approver_email, get_args, get_certificate_type
from common import is_san_request, get_approver_addresses, build_base_args
from settings import API_KEY, API_USERNAME, API_URL, CLIENT_IP



def parse_order_id_from_xml(input_xml):
    root = ET.fromstring(input_xml)
    success, errors = transaction_succeeded(input_xml)
    if success:
        return root.find('{http://api.namecheap.com/xml.response}CommandResponse/{http://api.namecheap.com/xml.response}SSLCreateResult/{http://api.namecheap.com/xml.response}SSLCertificate').attrib['CertificateID']
    else:
        return success, errors

def buy_ssl_cert(args):
    years = args.years
    base_args = build_base_args()
    command = 'Command=namecheap.ssl.create'
    request_dict = {
        'Command': 'namecheap.ssl.create',
        'Years': years,
        'Type': get_certificate_type(args),
    }
    base_args.update(request_dict)
    resp = requests.post(API_URL, params=base_args)
    api_response = resp.text
    order_id = parse_order_id_from_xml(api_response)
    # order_id = parse_order_id_from_xml(a)
    # api_response = example
    return order_id, api_response



def activate_ssl_cert(certificate_id, csr_text, args):
    request_dict = {
        'Command': 'namecheap.ssl.activate',
        'CertificateID': certificate_id,
        'csr': csr_text,
        'ApproverEmail': get_approver_email(args.common_name),
        'AdminEmailAddress': 'rtucker@mozilla.com'
    }
    if is_san_request(args):
        request_dict['DNSNAmes'] = args.san_names
        joined_emails = ",".join(get_approver_addresses(args))
        request_dict['DNSApproverEmails'] = joined_emails

    base_args = build_base_args()
    base_args.update(request_dict)
    resp = requests.post(API_URL, params=base_args)
    api_response = resp.text
    success, errors = transaction_succeeded(api_response)
    if not success:
        print("Unable to activate certificate. Errors: ")
        print(errors)


def main():
    args = get_args(sys.argv[1:])
    try:
        csr_text = open(args.csr_file, 'rb').read().decode()
    except:
        print('Error: Unable to read CSR file.')
        sys.exit(2)
    order_id, response = buy_ssl_cert(args)
    if order_id:
        print("Order ID: {}".format(order_id))
        activate_ssl_cert(order_id, csr_text, args)
    else:
        print("Unable to buy ssl cert. See error response below.")
        print(response)



if __name__ == '__main__':
    main()

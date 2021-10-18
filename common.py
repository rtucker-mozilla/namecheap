import xml.etree.ElementTree as ET
import argparse
from settings import API_KEY, API_USERNAME, CLIENT_IP

def build_base_args():
    # return "{}?ApiUser={}&ApiKey={}&UserName={}ClientIp={}".format(API_URL, API_USERNAME, API_KEY, API_USERNAME, CLIENT_IP)
    return {
        'ApiUser': API_USERNAME,
        'ApiKey': API_KEY,
        'UserName': API_USERNAME,
        'ClientIp': CLIENT_IP
    }

def get_args(args):
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', action='store',
                    dest='common_name',
                    help='Store a simple value')

    parser.add_argument('-y', action='store',
                    dest='years',
                    help='Store how many years to purchase certificate for.')

    parser.add_argument('-f', action='store',
                    dest='csr_file',
                    help='CSR Filepath.')

    parser.add_argument('-s', action='store',
                    dest='san_names',
                    help='Cert SANs excluding the common name')
    return parser.parse_args(args)

def get_approver_addresses(args):
    return_addresses = []
    sans = get_sans_from_args(args)
    for san in sans:
        email = get_approver_email(san)
        return_addresses.append(email)
    return return_addresses

def get_sans_from_args(args):
    tmp_san_names = args.san_names.replace(' ', '')
    return tmp_san_names.split(',')
    
def get_sans_from_args_as_string(args):
    tmp_san_names = args.san_names.replace(' ', '')
    return tmp_san_names.split(',')

def is_san_request(args):
    return get_san_count_from_args(args) > 0

def get_san_count_from_args(args):
    if args.san_names is None:
        return 0
    elif args.san_names == "":
        return 0
    sans = args.san_names.replace(" ", "")
    try:
        return len(sans.split(","))
    except:
        return 0

def get_certificate_type(args):
    san_count = get_san_count_from_args(args)
    if args.common_name.startswith('*'):
        return 'PositiveSSL Wildcard'
    elif san_count == 0 :
        return 'PositiveSSL'
    else:
        return 'PositiveSSL Multi Domain'

def get_approver_email(domain):
    if 'mozilla.org' in domain:
        return 'hostmaster@mozilla.org'
    elif 'mozilla.net' in domain:
        return 'hostmaster@mozilla.net'
    else:
        return 'hostmaster@mozilla.com'

def parse_errors(input_xml):
    root = ET.fromstring(input_xml)
    errors = root.find('{http://api.namecheap.com/xml.response}Errors')
    return_errors = []
    for error in [e.text for e in root.findall('{http://api.namecheap.com/xml.response}Errors/{http://api.namecheap.com/xml.response}Error')]:
        return_errors.append(error)
    return "\n".join(return_errors)

def transaction_succeeded(input_xml):
    success = False
    root = ET.fromstring(input_xml)
    try:
        if root.attrib['Status'] == 'OK':
            return True, None
    except:
        success = False

    if not success:
        errors = parse_errors(input_xml)
        return False, errors
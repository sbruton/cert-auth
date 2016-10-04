#!/usr/bin/env python

import argparse
import os
from string import Template

parser = argparse.ArgumentParser(description='Create and manage certificate authorities')
parser.add_argument('base_directory', nargs='?', help='base directory of certificate authority [default=CWD]', default=os.getcwd())
group = parser.add_mutually_exclusive_group()
group.add_argument('-c', '--create', help='create a new certifiate authority, will create an intermediate CA if a parent CA is provided with -p', action='store_true')
group.add_argument('-i', '--issue', metavar='CN', help='generate a new keypair and immediate issue a certificate')
parser.add_argument('-p', '--parent', metavar='PARENT', help='when creating a new certificate authority, create it as an intermediate under this specified existing CA')
args = parser.parse_args()

opensslConfigTemplateFile = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'openssl.cnf.tmpl')
baseDir = os.path.realpath(args.base_directory)
certsDir = os.path.join(baseDir, 'certs')
crlDir = os.path.join(baseDir, 'crl')
csrDir = os.path.join(baseDir, 'csr')
newCertsDir = os.path.join(baseDir, 'newcerts')
privateDir = os.path.join(baseDir, 'private')
indexFile = os.path.join(baseDir, 'index.txt')
serialFile = os.path.join(baseDir, 'serial')
opensslConfigFile = os.path.join(baseDir, 'openssl.cnf')
caKeyFile = os.path.join(privateDir, 'ca.key.pem')
caCertFile = os.path.join(certsDir, 'ca.cert.pem')
caCsrFile = os.path.join(csrDir, 'ca.csr.pem')

if args.create:
    if os.path.isfile(baseDir):
        raise Exception('Cannot create CA at {0}, not a directory'.format(baseDir))
    elif not(os.path.exists(baseDir)) or os.listdir(baseDir) == []:
        print 'creating a new ca at %s' % baseDir
        if not(os.path.exists(baseDir)):
            os.mkdir(baseDir)
        os.mkdir(certsDir)
        os.mkdir(crlDir)
        os.mkdir(csrDir)
        os.mkdir(newCertsDir)
        os.mkdir(privateDir)
        os.chmod(privateDir, 0o0700)
        open(indexFile, 'w').close()
        open(serialFile, 'w').write('1000')
        configTemplate = Template(open(opensslConfigTemplateFile, 'r').read())
        policy = 'strict'
        if args.parent:
            policy = 'loose'
        config = configTemplate.substitute(baseDir=os.path.realpath(baseDir), policy=policy)
        open(opensslConfigFile, 'w').write(config)
        os.system('openssl genrsa -out {0} 4096'.format(caKeyFile));
        os.chmod(caKeyFile, 0o0400)
        if not(args.parent):
            os.system('openssl req -config {0} -key {1} -new -x509 -days 7300 -extensions v3_ca -out {2}'.format(opensslConfigFile, caKeyFile, caCertFile))
        else:
            parentOpensslConfigFile = os.path.join(args.parent, 'openssl.cnf')
            os.system('openssl req -config {0} -key {1} -new -out {2}'.format(opensslConfigFile, caKeyFile, caCsrFile))
            os.system('openssl ca -config {0} -extensions v3_intermediate_ca -days 3650 -notext -in {1} -out {2}'.format(parentOpensslConfigFile, caCsrFile, caCertFile))
        os.chmod(caCertFile, 0o0444)
    else:
        raise Exception('Cannot create CA at {0}, directory not empty'.format(args.base_directory))
elif args.issue:
    print('issuing a certificate')
    keyFile = os.path.join(privateDir, '{0}.key.pem'.format(args.issue))
    csrFile = os.path.join(csrDir, '{0}.csr.pem'.format(args.issue))
    certFile = os.path.join(certsDir, '{0}.cert.pem'.format(args.issue))
    os.system('openssl genrsa -out {0} 2048'.format(keyFile))
    os.system('openssl req -config {0} -subj "/CN={1}" -key {2} -new -out {3}'.format(opensslConfigFile, args.issue, keyFile, csrFile))
    os.system('openssl ca -config {0} -extensions server_cert -notext -in {1} -out {2}'.format(opensslConfigFile, csrFile, certFile))
    os.chmod(certFile, 0o0444)
else:
    parser.print_help()

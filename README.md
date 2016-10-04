# cert-auth

Rapidly create root and intermediate certificate authorities and issue
certificates for development purposes

## Creating a New Root Certificate Authority

_Create a new CA in the current directory (must be empty)_
```sh
ca.py -c
```

_Create a new CA in a directory called rootCA_
```sh
ca.py -c rootCA
```

## Creating a New Intermediate Certificate Authority

_Create a new intermediate CA in intCA under another CA at rootCA_
```sh
ca.py -p rootCA -c intCA
```

## Issuing Certificates

_Create a new keypair and issue a certificate for test.com within a CA at /opt/ca/intCA_
```sh
ca.py -i test.com /opt/ca/intCA
```

# push-to-eurotermbank

ISOF's code for sending TBX files to Eurotermbank in the Federated
eTranslation TermBank Network Action.

The Federated eTranslation TermBank Network Action was co-financed by the Connecting Europe Facility of the European Union.
The contents of this documentation are the sole responsibility of the author and do not necessarily reflect the opinion of the European Union.

ISOF stores terminology in Rikstermbanken, which uses the NTRF
format. Contact sprakteknologi@isof.se for access to the conversion
code.

The code for pushing the TBX files to Eurotermbank is implemented
according to the Federated eTranslation TermBank Network Action
https://github.com/Eurotermbank/Federated-Network-Toolkit-deployment/blob/main/user-guides/synchronization.md


## First time
### Setup on Unix
The code uses the Python Requests library.
This needs to be installed (here it is done for a specific user)

```bash
export LC_ALL=C
python3 -m pip install --user requests
```

Eurotermbank only allows pushing from servers with a specific IP address. The address of the server must therefore be registrered with Eurotermbank.

A configuration files must be positioned in the same folder as `push_data.py`:
`configuration.py`.
The file `configuration_TEMPLATE.py` shows template content.

In the top folders with TBX files to be pushed, i.e. TBX_files_ready_to_push and TBX_files_not_in_rikstermbanken_ready_to_push, there needs to be a json autentication file. (As the authentication is different for the two different folders, two different authentication files are needed)
`authentication.json`  

The file `authentication_TEMPLATE.py` shows template content.

The company Tilde (which runs Eurotermbank) provides information
needed for authentication and configuration.


## Push the data
Run with the command
```python
python3 push_data.py <directory with content to push>
```
For instance:
```python
python3 push_data.py ../TBX_files_ready_to_push/3548
```
or
```python
python3 push_data.py ../TBX_files_not_in_rikstermbanken_ready_to_push/999001
```

## Delete previously pushed collections
To delete previously pushed collections, run the command
```python
python3 push_data.py <directory with content to push> DEL
```

For instance:
```python
python3 push_data.py ../TBX_files_ready_to_push/3548 DEL
```

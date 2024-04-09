# NTRF2TBX

Python code for exporting data from NTRF format to TBX format.

## To import content in MongoDB
### The first time
#### Get and configure the code for importing to the database
```
git clone git@github.com:sprakradet/rikstermbanken-web.git main
```
Create the file `src/updatecfg.py` as follows:
```
MONGODB_USERNAME = None
MONGODB_PASSWORD = None
MONGODB_DB = ""
```

#### Prepare the database

```
conda install -c anaconda pymongo
conda install -c anaconda mongodb
```
Create the directory where the database data is to be saved, e.g., `data/db` 
If you also want to export non-Rikstermbanken NTRF files, also create a directory where the database data for those files are to be saved, e.g., `data/db-non-rtb` 

### Each time
Start the server giving the directory where data is to be saved as a parameter (unless the server is already running) 
```
mongod --dbpath data/db/ 
```
or
```
mongod --dbpath data/db-non-rtb/ 
```

(mongodb listens as default on port 27017.)

In the directory `rikstermbanken-web' run
```
python src/import_bankvalvet.py <search path to NTRF_files_with_open_license>
```

or 

```
python src/import_bankvalvet.py <search path to NTRF_files_not_in_rikstermbanken>
```

For instance:
```
python src/import_bankvalvet.py ../tbx-conversion/NTRF_files_with_open_license
```
For the import, it is checked whether the git repository in the content of the folder  `<search path to NTRF_files_with_open_license>`
has a new version compared to when it was last updated. If that is not the case, no new import will be carried out.


## Usage, i.e. how to run the tbx conversion
The code is run by (in the same directory as the file `create_eurotermbank_folder.py`) writing:
(TBX_files_ready_to_push is the folder to which the data is written.)

```
python create_eurotermbank_folder.py <id of collection to convert> <output folder>
```
For instance:
```
python create_eurotermbank_folder.py 3548 TBX_files_ready_to_push
```

or

```
python create_eurotermbank_folder.py 989001 TBX_files_not_in_rikstermbanken_ready_to_push
```

This will write a test tbx to TBX_files_ready_to_push

## Write metadata files
When the TBX files are generated, a template-file for metadata is also created, called `TEMPLATE_<nr>_metadata.json`, e.g.
`TEMPLATE_989001_metadata.json`
This file must be renamed to `metadata.json`, and metadata needs to be provided.
Note that a correct ''domainid'' is necessary. No clear error messages will be given if the domainid is incorrrect.
https://github.com/Eurotermbank/Federated-Network-Toolkit-deployment/blob/5918fe4486eac2f9f4067043b1cad9639d14a230/user-guides/DomainClassifiers.md



The file `configuration.py` states how many terms to have in each TBX file. As Eurotermbank only allows 100 terms in each TBX file, this is now set to 100. But if the conversion is to be used for something else, it might be more practical to generate one TBX for each NTRF.
Then change the `configuration.py` to

`TERM_BATCH_SIZE = None`

## Push to Eurotermbank
The next step, when having created a tbx file is to push the TBX files to
Eurotermbank. This code is in the folder push-to-eurotermbank.
See the README in that folder for more information.

## Overview of the code
`create_tbx.py`: The main code, and also the logic for converting to TBX.

`get_from_db.py`: Convert and prepare the data fetched from the database to make it easy to handle in create_tbx.py.

`db_info_tuples.py`: For storing the data in get_from_db.py.

`fetch_from_db.py`: The communication with the database.

`read_tbx.py`: Only start of the code for converting from TBX to the interal format of Rikstermbanken.


## How to deploy
### First time
Put eurotermbank and eurotermbank.pub in your .ssh folder

create fedterm environment

```
miniconda3/condabin/conda create fedterm
```
```
conda install -c anaconda requests
```

### Each time (to log in with the eurotermbank user)

```
ssh -i ~/.ssh/eurotermbank eurotermbank@<deployed server>
```

```
conda activate fedterm
```

```
cd tbx-conversion
```

```
git pull
```

Then do push, according to README.md in `push-to-eurotermbank`

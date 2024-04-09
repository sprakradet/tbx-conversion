# How to run the regression test

You need to have, an having i the repository rikstermbanken-web (see the main)

## Remove the regression test database
Remove content in regressiontest_db, but keep the directory.
(Or if nothing has changed, keep it, and skip the "Import the data to the database" step)

## Start the regression test database
Note, the point is that this should be another database than the one used for the export. 
First, make sure no other database is running. Then write the following
```
    mongod  --dbpath <current_dir>/regressiontest_db
```
For instance:
```
     mongod --dbpath tbx-conversion/regressiontest/regressiontest_db
```

## Import the data to the database
In the directory `rikstermbanken-web' 

Run:
```
python src/import_bankvalvet.py <the search path to the directory regressiontest_ntrf>
```
Ex:
```
python src/import_bankvalvet.py ../tbx-conversion/regressiontest/regressiontest_ntrf/
```
## Remove the content in regressiontest_output

Remove the content in the directory `regressiontest_output`
## Run
Standing in the directory regressiontest, run
```
sh run_regressiontest.sh
```
## Shut down the database
Shut down the database

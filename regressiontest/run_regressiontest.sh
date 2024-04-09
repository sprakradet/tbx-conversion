#!/usr/bin/env bash

echo
echo "*******************************************"
python ../create_eurotermbank_folder.py 9999991 regressiontest_output

echo
echo "Diff for 9999991_1.tbx:"
echo "------------------------"
diff regressiontest_expected_output/9999991/9999991_1.tbx regressiontest_output/9999991/9999991_1.tbx

echo
echo "Diff for TEMPLATE_9999991_metadata.json:"
echo "-----------------------------------------"
diff regressiontest_expected_output/9999991/TEMPLATE_9999991_metadata.json regressiontest_output/9999991/TEMPLATE_9999991_metadata.json
echo
echo
echo
echo


python ../create_eurotermbank_folder.py 9999992 regressiontest_output

echo
echo "Diff for 9999992_1.tbx:"
echo "------------------------"
diff regressiontest_expected_output/9999992/9999992_1.tbx regressiontest_output/9999992/9999992_1.tbx

echo
echo "Diff for TEMPLATE_9999992_metadata.json:"
echo "-----------------------------------------"
diff regressiontest_expected_output/9999992/TEMPLATE_9999992_metadata.json regressiontest_output/9999992/TEMPLATE_9999992_metadata.json

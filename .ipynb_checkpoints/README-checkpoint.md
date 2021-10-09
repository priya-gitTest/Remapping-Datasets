# Remapping Datasets

## What is new (2021-10-09)
- Swap function added: A->B and B->A
- Date conversion function added: converts a date format into ISO8601 (%Y-%m-%d)
- Duration function added: duration between two valid ISO8601 dates

## Video links
- Short version: https://youtu.be/xTrYKaCdxC0
- Detailed version: https://youtu.be/LTvXEqFve1E

## Requirements
* no coding required, only requirement is to run a python script or a Jupyter Notebook (so either python or jupyter must be installed)
** pandas and openpyxl must be installed
* all mapping and onfigurations via the included Excel

## How to use
For how to use it, see the instructions in the table Explanation in conversion.xlsx
* Jupyter Notebook: it will ask which Excel to use for mapping & configuration
* From command line: python conversion.py conversion.xlsx (other Excel can be used)

## What it can do
- You can have multiple conversion.xlsx; each with its unique name, own mapping & configuration
- Substitute IDs based on key list
- Swap variables: A->B and B->A
- Date conversion: give a date format (e.g. %m/%d/%Y and this will be converted to %Y-%m-%d (ISO8601)
     Keep in mind: small caps for m (Month) and d (Day), always at % in front of it, divisor '-', '/', etc
     can be anything. Errors will be displayed int the output with: ERR: <original value>
- Add variable containing duration in days based on two valid ISO8601 dates
- Remap variables with or without value conversion
- Remap Option group Variables to Check Box group Variables (granted only one option can be remapped per entry)
- Remap Check Box group Variables to Option group Variables (when multi check box, then the 'option' group gets multi options comma seperated)
- Add unit variables (e.g. add variable Temperature_Unit = 1 (could be Celcius) when source variable has a value, empty when empty
- Removes all 'redudant' variables (non mapped variables in source)
- Orders the variables based on the Excel order list of target variables

## The output
Remapping creates a time stamped:
- CSV, and
- Excel

# micro-portraits

This repository contains code to extract microportraits.

Language covered: Dutch

Required input: NAF files containing the following layers:

- terms
- deps
- coreference (entities)

Output: csv files with descriptions.
Descriptions for the same entity share an identifier.

This work is described in:

Fokkens, Antske, Nel Ruigrok, Camiel J. Beukeboom, Gagestein Sarah, and Wouter Van Attveldt. 
"Studying Muslim Stereotyping through Microportrait Extraction." In LREC. 2018.

Running the code:

python -m microportraits inputfile.naf > outputfile.csv




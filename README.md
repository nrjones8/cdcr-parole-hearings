## Data description
The [CDCR](http://www.cdcr.ca.gov/) (California Department of Corrections and Rehabilitation) publishes data about parole hearing results. These datasets are published in PDF format, and posted to the CDCR website. Separate PDFs are difficult to analyze; this project parses those PDFs (currently, just the yearly hearings from 2012 through 2017), and combines their data into an analysis-friendly CSV.

* [CSV of Parole hearing results, 2012-2017](https://raw.githubusercontent.com/nrjones8/cdcr-parole-hearings/master/data/2012_to_2017_hearings.csv)
* [CDCR page](https://www.cdcr.ca.gov/BOPH/pshResults.html) with raw PDF results

This project was inspired by [The Parole Hearing Data Project](http://www.parolehearingdata.org/), which compiled a similar, more comprehensive dataset of parole hearings in New York State. The data and code for that project are also available [on Github](https://github.com/rcackerman/parole-hearing-data).

## Details on the data
The combined dataset is based on the raw PDFs that the CDCR has published; thus, all fields are defined by the CDCR - this project just formats them in an easier-to-use way. The columns in the dataset are described below:
* `cdc_num` - the internal ID used by the CDCR to track people up for parole
* `county_of_comittment` - my understanding is that this field indicates which county the original crime was committed in, but the CDCR website does not give further information on this field
* `gov_review_authority` - This field refers to a governor's authority to review a decision made by the parole board. When present, it is either `3041.1` or `3041.2`, each of which refers to specific sections of the California penal code. See [Decision Review and Governor’s Review](https://www.cdcr.ca.gov/BOPH/docs/Policy/Decision_Review_and_Governor.pdf) from the CDCR's website for further explanation.
* `hearing_date` - date of the hearing
* `hearing_type` - was it an initial or subsequent hearing? "INITIAL" indicates an initial (first) hearing. "SUB X" indicates that there this is the Xth subsequent hearing. E.g. "SUB 2" indicates that there was already an initial hearing, a first subsequent hearing, and now a second subsequent hearing.
* `result` - The outcome of the hearing. The CDCR site explains these in more detail [here](https://www.cdcr.ca.gov/BOPH/pshResults.html); their definitions are reproduced below:
    * `Grant` – The inmate was found suitable for parole and, therefore, was granted parole.

    * `Deny` – The inmate was not found suitable and, therefore, was denied parole.

    * `Continue` - The hearing was started, but could not be completed for some reason. It will be scheduled for completion at a future date.

    * `Cancelled` – The parole hearing was cancelled. A parole-hearing is cancelled when there is no need for the hearing to go forward and it does not need to be rescheduled. For example, a hearing will be cancelled if the inmate was released pursuant to a court order or if the inmate dies. In these situations, the hearing is not "continued" or "postponed" because the hearing will not be rescheduled.

    * `Split` – The parole hearing resulted in a split decision. A split decision occurs when the members of a two-person parole hearing panel do not agree on (1) whether an inmate is suitable for parole, or (2) the length of a denial period (15, 10, 10, 7, 5, or 3 years) for an inmate who is unsuitable for parole.

    * `Postpone` – The hearing was postponed. The board may postpone a hearing on its own motion, at the request of an inmate, or for exigent circumstances. Sometimes postponements are requested days or weeks before the scheduled hearing date, but postponements may also occur on the day of a hearing.

    * `Waive` – The inmate waived his or her right to a hearing. An inmate may waive his or her right to a parole hearing for any reason for a period of one to five years as long as the request is submitted at least 45 calendar days prior to the hearing. A request to waive a hearing submitted less than 45 days before a hearing will be denied unless good cause is shown and the reasons for the waiver were not and could not reasonably have been known to the inmate 45 days prior to the hearing.

    * `Stip` – The inmate stipulated to being unsuitable and was denied parole without a parole hearing being held. A stipulation occurs when the board accepts an inmate’s offer to stipulate to his or her unsuitability for parole for a specified period (15, 10, 7,  5, or 3 years). If the board accepts an inmate’s offer to stipulate, it is considered a denial of parole for the stipulated period.
* `length` - If the person was not granted parole, how much time until their next hearing? E.g. "11 mo" indicates that the next hearing will happen in 11 months.


## Technical details
Parsing of PDFs is done by the extremely helpful [Tabula](http://tabula.technology/) tool. You can read more specifically on how it can be used from the command line [here](https://github.com/tabulapdf/tabula-java/wiki/Using-the-command-line-tabula-extractor-tool). The `.jar` necessary for running Tabula from the command line has been checked into this repo (tabula-1.0.1-jar-with-dependencies.jar).

To run the parser:
```
python hearingscraper/assemble_data.py
```
which will show output about what is being run, like so:
```
...
Running: java -jar tabula-1.0.1-jar-with-dependencies.jar -p all -a 85.26,26.53,770.86,576.54 -o data/tabula-raw-exported-command-line/PSHR_2012.csv data/raw-hearings-pdfs/PSHR_2012.pdf
...
```

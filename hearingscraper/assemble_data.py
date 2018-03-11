import csv
import os
import subprocess

# Thank you to: https://github.com/tabulapdf/tabula-java/wiki/Using-the-command-line-tabula-extractor-tool
TABULA_CMD = 'java -jar tabula-1.0.1-jar-with-dependencies.jar -p all -a {y1},{x1},{y2},{x2} -o {csvfile} {pdfname}'

# Where the source PDFs live
PDFS_PATH = 'data/raw-hearings-pdfs'
# This directory stores out the output of running tabula on individual PDFs - that output has not
# been altered at all.
PARSED_CSVS_PATH = 'data/tabula-raw-exported-command-line'

ALL_YEARS_HEARINGS_PATH = 'data/2012_to_2017_hearings.csv'

# Just hard-code these for now, could actually read the dir later if doing weekly PDFs
YEARS_TO_PROCESS = [
    'PSHR_2012',
    'PSHR_2013',
    'PSHR_2014',
    'PSHR_2015',
    'PSHR_2016',
    'PSHR_2017'
]

COLUMN_NAMES_WITH_LAST_NAME = [
    'last_name',
    'cdc_num',
    'county_of_comittment',
    'gov_review_authority',
    'hearing_date',
    'hearing_type',
    'result',
    'length'
]

# Same column names as above, just remove the `last_name`. There's no need for it in the output,
# and I think it's best to remove at least that piece of identifying information. The `cdc_num` may
# be helpful for people to look up individual cases (and obviously as a way to see the various
# hearings that one person has had).
COLUMN_NAMES_NO_LAST_NAME = [c for c in COLUMN_NAMES_WITH_LAST_NAME if c != 'last_name']

# These were taken from Preview, following the (extremely helpful) directions here:
# https://github.com/tabulapdf/tabula-java/wiki/Using-the-command-line-tabula-extractor-tool
Y1 = 85.26
X1 = 26.53
Y2 = 770.86
X2 = 576.54


def prepend_line_to_file(file_path, line_to_prepend):
    # There are probably better ways to do this :shrug:
    with open(file_path, 'r') as f:
        lines_to_write = f.readlines()

    lines_to_write.insert(0, line_to_prepend)

    with open(file_path, 'w') as f:
        f.writelines(lines_to_write)

def combine_csvs(combined_path):
    """
    Reads all the written CSVs (according to PARSED_CSVS_PATH), and combines them into one CSV with all
    hearings. Writes the output to `combined_path`
    """
    all_hearings = []
    for year in YEARS_TO_PROCESS:
        one_csv = '{}/{}.csv'.format(PARSED_CSVS_PATH, year)
        with open(one_csv) as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                all_hearings.append(row)

    print 'Collected {} hearings in total'.format(len(all_hearings))

    with open(combined_path, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=COLUMN_NAMES_NO_LAST_NAME)
        writer.writeheader()

        for hearing in all_hearings:
            writer.writerow(hearing)

    print 'Wrote combined out to {}'.format(combined_path)

    with open(combined_path, 'r') as f:
        combined_output_lines = f.readlines()

    total_lines_in_combined_output = len(combined_output_lines)
    if total_lines_in_combined_output == len(all_hearings) + 1:
        # One header line, plus all the hearing lines
        print 'Got the expected number of lines in output, {}'.format(total_lines_in_combined_output)
    else:
        print 'Output looks off - read {} lines from combined file, but had {} cases'.format(
            total_lines_in_combined_output, len(all_hearings)
        )

def clean_raw_csv(csv_path):
    """
    1. Removes the `last_name` column in the CSV present at `csv_path`
    2. Removes any entry that lacks a `cdc_num` entry (it was likely not parsed correctly by tabula)

    Overwrites the content of `csv_path`.
    """
    data_with_last_names = []
    with open(csv_path) as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            data_with_last_names.append(row)

    without_last_names = []
    for row in data_with_last_names:
        # Skip any row that's missing a CDC number
        cdc_num = row['cdc_num']
        if cdc_num != '' and cdc_num is not None:
            without_last_names.append({k: v for k, v in row.iteritems() if k != 'last_name'})

    with open(csv_path, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=COLUMN_NAMES_NO_LAST_NAME)
        writer.writeheader()

        for row in without_last_names:
            writer.writerow(row)

    print 'Overwrote {} to not have last names. Total of {} hearings.'.format(
        csv_path, len(without_last_names)
    )


def process_raw_pdfs(years):
    """
    Processes `years` worth of hearings:
    1. Runs tabula on a given year's PDF of hearings, which outputs a CSV
    2. Edits that CSV to remove the `last_name` column
    3. Combines those individual CSVs into one that contains all years worth of data
    """
    for year in years:
        one_pdf_path = '{}/{}.pdf'.format(PDFS_PATH, year)
        one_csv_path = '{}/{}.csv'.format(PARSED_CSVS_PATH, year)
        full_cmd = TABULA_CMD.format(**{
            'y1': Y1,
            'x1': X1,
            'y2': Y2,
            'x2': X2,
            'pdfname': one_pdf_path,
            'csvfile': one_csv_path
        })
        print 'Running: {}'.format(full_cmd)
        # There are some errors from each run of `tabula`, but they're basically fine to ignore -
        # they pop up from trying to parse "title" lines that are of a different format than the
        # actual data
        with open(os.devnull, 'w') as devnull:
            # Thank you https://stackoverflow.com/a/14736249
            subprocess.call(full_cmd, shell=True, stdout=devnull, stderr=devnull)

        header_line = ','.join(COLUMN_NAMES_WITH_LAST_NAME) + '\n'
        prepend_line_to_file(one_csv_path, header_line)
        clean_raw_csv(one_csv_path)

def main():
    process_raw_pdfs(YEARS_TO_PROCESS)
    combine_csvs(ALL_YEARS_HEARINGS_PATH)

if __name__ == '__main__':
    main()

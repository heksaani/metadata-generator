# Metadata Generator

To avoid manual labor, this script generates a metadata CSV file (`metadata.csv`)
for the [InnuendoCLI](https://github.com/yetulaxman/InnuendoCliCpouta) pipeline.

It scans a folder (and its subfolders) for paired-end `.fastq.gz` files, asks the
user for the required metadata fields, and writes them out in the format expected
by InnuendoCLI (`;`-delimited CSV with a `#Pipeline-Species;...` header).

## Requirements

- Python 3.9+
- No external dependencies for running the script itself
- [`pytest`](https://docs.pytest.org/) if you want to run the test suite

## Usage

Run the script and follow the prompts:

```bash
python3 metadata_generator.py
```

The script will:

1. Ask for the path to the folder containing your `.fastq.gz` files.
   - Files are matched into sample pairs based on `_R1` / `_R2` in the filename
     (e.g. `SAMPLE1_R1.fastq.gz` + `SAMPLE1_R2.fastq.gz` → sample `SAMPLE1`).
   - Subfolders are searched recursively.
   - Samples missing either the R1 or R2 file are skipped with a warning.
   example: 
   ``` /path/to/fastq_folder ```
2. Let you optionally set **common values** (Species, Source, Owner-Collection,
   Instrument) that will be applied to every sample. Leave a field empty to be
   asked for it separately for each sample instead.
3. Ask for the remaining metadata for each sample individually.
4. Write `metadata.csv` into the fastq folder you provided in step 1.

> **Note:** the metadata file must live in the same folder as the raw data when
> you launch the InnuendoCLI pipeline — this script places it there automatically.

## Metadata fields

| Column | Field | Requirement |
|---|---|---|
| 1 | Pipeline-Species | Compulsory, fixed list |
| 2 | Primary-Identifier | Compulsory (derived from filename) |
| 3 | RYMY-ID | Optional |
| 4 | Food_bug | Optional |
| 5 | Source | Compulsory, fixed list |
| 6 | Sampling-Reason | Optional, fixed list |
| 7 | Sampling-Date | Conditionally optional* |
| 8 | Sample-Received-Date | Conditionally optional* |
| 9 | Owner-Collection | Compulsory, fixed list |
| 10 | Location | Optional, fixed list |
| 11 | AMR-Phenotype | Optional, fixed list |
| 12 | Additional-Information | Optional |
| 13–14 | File_1 / File_2 | Compulsory (found automatically) |
| 15 | Accession | Optional |
| 16 | Instrument | Optional, fixed list |
| 17 | Library | Fixed list |
| 18 | Library-Other | Only asked if Library = "Other" |
| 19 | Add-Results | y/n, defaults to "n" if left empty |

\* At least one of Sampling-Date or Sample-Received-Date must be provided.

Valid values for each fixed-list field are defined at the top of the script
(`valid_species_names`, `valid_source`, `valid_owner`, etc.) and follow the
[InnuendoCliCpouta MetadataVocab](https://github.com/yetulaxman/InnuendoCliCpouta/tree/main/MetadataVocab)
definitions.

## Example output

```
#Pipeline-Species;Primary-Identifier;RYMY-ID;...;Library;Library-Other;Add-Results
Escherichia coli;SAMPLE1;124;...;Nextera XT;;y
```

## Running the tests

```bash
pip install pytest
pytest test_metadata_script.py -v
```

The test suite covers input validation, date validation, sample-pair detection
from fastq filenames, and a full end-to-end run of the script with simulated
user input.

"""Python script to make the metadata template for Innuendo pipeline.
The script will ask the user to give the path to the folder that contains fastq files.
Then it will ask the user to give metadata information for each sample.
Finally, it will write the metadata information to a csv file called metadata.csv
# Column 1: pipeline species (compulsory, set terms)
# Column 2: primary_identifier (compulsory)
# Column 3: RYMY-ID (optional)
# Column 4: Food_bug (optional)
# Column 5: Source (compulsory, set terms)
# Column 6: Sampling reason (optional, set terms)
# Columns 7-8: Sampling-Date, Sample-Received-Date (conditionally optional)
# Column 9: Owner-Collection (compulsory, set terms)
# skipped in template; Column 10: Submitter-Sample
# skipped in template ; Column 11: Submitter-Database
# Column 12: Location (optional, set terms)
# Column 13: AMR-Phenotype (optional, set terms)
# Column 14: Additional-Information (optional)
# Columns 15-16: Read files
# Column 17: Accession (Optional)
# Column 18: Instrument (optional, set terms)
# Column 19: Library
# Column 20: Library-Other
# Column 21: Write reports (If omitted, assume "n". )
"""
from pathlib import Path
from collections import defaultdict
from typing import Optional, List, DefaultDict
import csv, os
from datetime import datetime
from dataclasses import dataclass
import re

@dataclass
class Field:
    """Class to represent a metadata field with its properties.
    
    key: The name of the attribute in the Metadata class.
    question: The question to ask the user for this field.
    options: Optional list of valid options for this field (if applicable).
    mandatory: Whether this field is mandatory or not.
    """
    key: str                 # Metadata-luokan attribuutin nimi
    question: str
    options: Optional[List[str]] = None
    mandatory: bool = False
    is_date: bool = False
    allow_common: bool = False

valid_species_names = ["Escherichia coli",
"Campylobacter jejuni",
"Salmonella enterica",
"Yersinia enterocolitica",
"Yersinia pseudotuberculosis",
"Listeria monocytogenes",
"Staphylococcus aureus"]

valid_source = ["Human",
"Food",
"Feed",
"Animal",
"Animal,cattle",
"Animal,poultry",
"Animal,swine",
"Animal,other",
"Environment",
"Water",
"Other",
"Unknown",
"Confidential"]

valid_owner = ["THL",
"Ruokavirasto, HMIK",
"Ruokavirasto, HRES",
"Ruokavirasto, KBAK",
"Ruokavirasto, HBAK",
"Other"]

valid_location = ["Finland", 
            "Non-domestic",
            "Unknown"]

valid_library = ["Nextera XT",
"Illumina DNA Prep",
"Other"]

valid_amr_phenotype = ["ESBL",
"Colistin resistant",
"AmpC",
"CPE",
"MRSA" ]
valid_sampling_reason = ["In-house control",
"Control by the authorities",
"Outbreak investigation",
"Zoonoses monitoring or control program",
"Antimicrobial resistance monitoring",
"Research project",
"Proficiency test or external quality assessment",
"Reference laboratory activities",
"Other"]

valid_instruments = [
"HiSeq X Five",
"HiSeq X Ten",
"Illumina Genome Analyzer",
"Illumina Genome Analyzer II",
"Illumina Genome Analyzer IIx",
"Illumina HiScanSQ",
"Illumina HiSeq 1000",
"Illumina HiSeq 1500",
"Illumina HiSeq 2000",
"Illumina HiSeq 2500",
"Illumina HiSeq 3000",
"Illumina HiSeq 4000",
"Illumina HiSeq X",
"Illumina MiSeq",
"Illumina MiniSeq",
"Illumina NovaSeq 6000",
"Illumina NovaSeq X",
"Illumina iSeq 100",
"NextSeq 1000",
"NextSeq 2000",
"NextSeq 500",
"NextSeq 550",
"unspecified"]

FIELD_DEFS = [
    Field("species",   "Enter Species:", valid_species_names, mandatory=True, allow_common=True),
    Field("rymy_id",   "Enter RYMY-ID:"),
    Field("food_bug",  "Enter Food_bug:"),
    Field("source",    "Enter Source:", valid_source, mandatory=True, allow_common=True),
    Field("sampling_reason", "Enter Sampling-Reason:", valid_sampling_reason),
    # sampling_date / sample_received_date käsitellään erikseen (conditionally optional)
    Field("owner", "Enter Owner-Collection:", valid_owner, mandatory=True, allow_common=True),
    Field("location",   "Enter Location (case sensitive):", valid_location),
    Field("amr_phenotype", "Enter AMR-Phenotype:", valid_amr_phenotype),
    Field("additional_information", "Enter Additional-Information:"),
    Field("accession",  "Enter Accession:"),
    Field("instrument", "Enter Instrument:", valid_instruments, allow_common=True),
    Field("library",    "Enter Library:", valid_library),
]
output_columns = ["#Pipeline-Species",
                    "Primary-Identifier",
                    "RYMY-ID",
                    "Food_bug",
                    "Source",
                    "Sampling-Reason",
                    "Sampling-Date",
                    "Sample-Received-Date",
                    "Owner-Collection",
                    "Location",
                    "AMR-Phenotype",
                    "Additional-Information",
                    "File_1",
                    "File_2",
                    "Accession",
                    "Instrument",
                    "Library",
                    "Library-Other",
                    "Add-Results"]

questions = ["Enter Species: (mandatory)", 
             "Enter RYMY-ID:",
             "Enter Food_bug:",
             "Enter Source (e.g., Human):",
             "Enter Sampling-Reason:",
             "Enter Sampling-Date (YYYY-MM-DD):",
             "Enter Sample-Received-Date (YYYY-MM-DD):",
             "Enter Owner-Collection (your organization):",
             "Enter Location (e.g., Finland) this is case sensitive:",
             "Enter AMR-Phenotype:", "Enter Additional-Information:",
             "Enter Accession:", "Enter Instrument:",
             "Enter Library:", "Enter Library-Other:", "Add Results to DB? (y/n):"]


# Column 1: pipeline species (compulsory, set terms)
# Column 2: primary_identifier (compulsory)
# Column 3: RYMY-ID (optional)
# Column 4: Food_bug (optional)
# Column 5: Source (compulsory, set terms)
# Column 6: Sampling reason (optional, set terms)
# Columns 7-8: Sampling-Date, Sample-Received-Date (conditionally optional)
# Column 9: Owner-Collection (compulsory, set terms)
# skipped in template; Column 10: Submitter-Sample
# skipped in template ; Column 11: Submitter-Database
# Column 12: Location (optional, set terms)
# Column 13: AMR-Phenotype (optional, set terms)
# Column 14: Additional-Information (optional)
# Columns 15-16: Read files
# Column 17: Accession (Optional)
# Column 18: Instrument (optional, set terms)
# Column 19: Library
# Column 20: Library-Other
# Column 21: Write reports (If omitted, assume "n". )


class Metadata:
    def __init__(self, species:str, identifier:str, rymy_id:str, food_bug:str, source:str,
                 sampling_reason:str, sampling_date:str, sample_received_date:str,
                 owner:str, location:str, amr_phenotype:str, additional_information:str, file1:str, file2:str,
                 accession:str, instrument:str, library:str, library_other:str, add_results:str):
        """Initialization of the metadata class which has the following information
        species:
        identifier:
        rymy_id:
        food_bug
        source:
        sampling_data:
        sample_received_date:
        owner:
        location:
        file1:
        file2:
        accession:
        instrument:
        library:
        library-other:
        add_results:
        """
        self.species = species
        self.identifier = identifier
        self.rymy_id = rymy_id
        self.food_bug = food_bug
        self.source = source
        self.sampling_reason = sampling_reason
        self.sampling_date = sampling_date
        self.sample_received_date = sample_received_date
        self.owner = owner
        self.location = location
        self.amr_phenotype = amr_phenotype
        self.additional_information = additional_information
        self.file1 = file1
        self.file2 = file2
        self.accession = accession
        self.instrument = instrument
        self.library = library
        self.library_other = library_other
        self.add_results= add_results

    def to_list(self):
        """Returns the metadata as a list of fields for CSV writing"""
        return [self.species, self.identifier, self.rymy_id, self.food_bug, self.source,
                self.sampling_reason, self.sampling_date, self.sample_received_date,
                self.owner, self.location, self.amr_phenotype, self.additional_information,
                self.file1, self.file2, self.accession, self.instrument, self.library, self.library_other,
                self.add_results]
    
    @staticmethod
    def header_exists(filename: str) -> bool:
        if not os.path.isfile(filename):
            return False
        with open(filename, 'r') as f:
            first_line = f.readline().strip()
            return first_line.startswith("#Pipeline-Species;")

    @staticmethod
    def write_to_csv(filename:str, metadata_list:list):
        """Writes the metadata to a CSV file with the specified filename.
        If the file already exists, it will append the new metadata to the existing file.
        """
        with open(filename, "w", newline='') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(output_columns)
                for meta in metadata_list:
                    writer.writerow(meta.to_list())

# Illuminan bcl2fastq-oletusnimeäminen: <näyte>_S<numero>_L<lane>_R<1|2>_001.fastq.gz
ILLUMINA_PATTERN = re.compile(
    r'^(?P<sample>.+)_S\d+_L\d{3}_R(?P<read>[12])_\d+\.fastq\.gz$', re.IGNORECASE
)

# Yksinkertaisempi muoto: <näyte>_R<1|2>[valinnainen loppu].fastq.gz
SIMPLE_PATTERN = re.compile(
    r'^(?P<sample>.+?)_R(?P<read>[12])(?:_\d+)?\.fastq\.gz$', re.IGNORECASE
)


def parse_fastq_filename(filename: str):
    """Palauttaa (sample_id, read_number) tai (None, None) jos ei täsmää."""
    for pattern in (ILLUMINA_PATTERN, SIMPLE_PATTERN):
        match = pattern.match(filename)
        if match:
            return match.group("sample"), match.group("read")
    return None, None


def create_sample_dictionary(sample_fastq_folder: str) -> DefaultDict[str, List[Optional[Path]]]:
    """..."""
    base_dir = Path(sample_fastq_folder)
    fastq_files = list(base_dir.rglob('*.fastq.gz'))
    if not fastq_files:
        print(f"ERROR: No fastq.gz files found in the folder {sample_fastq_folder}")
        return defaultdict(lambda: [None, None])

    sample_dict: DefaultDict[str, List[Optional[Path]]] = defaultdict(lambda: [None, None])

    for file in fastq_files:
        identifier, read_num = parse_fastq_filename(file.name)
        if identifier is None:
            print(f"ERROR the file {file} name does not match expected R1/R2 naming pattern")
            continue

        idx = 0 if read_num == "1" else 1
        existing = sample_dict[identifier][idx]
        if existing is not None:
            print(f"WARNING: multiple R{read_num} files matched identifier '{identifier}': "
                f"{existing.name} and {file.name}. Using the latter.")
        sample_dict[identifier][idx] = file

    return sample_dict

def validate_input(user_input, valid_options):
    "Check if the user input is valid for the pipeline"
    if valid_options is None:
        return True
    if user_input not in valid_options:
        print(f"Invalid input. Please choose from {valid_options}.")
        return False
    return True

def validate_date(value):
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        print("Invalid date, use format YYYY-MM-DD.")
        return False

def ask_from_user(question, valid_options=None, mandatory = False, is_date=False):
    while True:
        user_input = input(question + " ").strip()
        if user_input == "":
            if mandatory:
                print("This field is mandatory.")
                continue
            return ""          # optional and empty
        if not validate_input(user_input, valid_options):
            continue
        if is_date and not validate_date(user_input):
            continue
        return user_input

def main():

    print("This script works as follows:\n" \
    "1. User is asked to give the path to the folder that contains fastq files.\n" \
    "2. You can set some of the metadata to be same for all samples\n" \
    "3. Then user is asked to give metadata information for each sample.\n" \
    "4. Finally, the script will write the metadata information to a csv file called metadata.csv\n" \
    "\n"
    "Compulsory fields are:\n" \
    "Pipeline-Species\nPrimary-Identifier\nSource\nOwner-Collection.\n" \
    "Sampling-Date and Sample-Received-Date are conditionally optional meaning one of them must be given.\n" )
    print("")
    while True:
        sample_fastq_folder= input("Give the path to folder where sample fastq files are located: ")
        if not sample_fastq_folder:
            print("Path cannot be empty.")
            continue
        if not Path(sample_fastq_folder).is_dir():
            print(f"'{sample_fastq_folder}' is not a valid directory.")
            continue
        sample_dict = create_sample_dictionary(sample_fastq_folder)
        if not sample_dict:
            print("No samples found please check the path and try again.")
        else:
            break
              
    metadata_list = [] # list to hold Metadata objects
    
    
    print(f"\nFound {len(sample_dict)} samples in the folder {sample_fastq_folder}.")

    print("--------------------------------------------------------------------------------")
    common_values = {}

    print("\n--- You can give common values for all samples. Leave empty if you want to ask separately for each sample. ---\n")
    for f in FIELD_DEFS:
        if f.allow_common:
            common_values[f.key] = ask_from_user(
                f"Give common value for '{f.key}' or leave empty to ask per sample:",
                valid_options=f.options, mandatory=False)

    for sample_id, files in sample_dict.items():
        r1, r2 = files[0], files[1]
        if r1 is None or r2 is None:
            print(f"ERROR: Sample {sample_id} does not have both R1 and R2 fastq files. Skipping this sample.")
            continue

        print(f"\nFor sample {sample_id} input the following metadata (leave blank if not available)")
        values = {}
        for f in FIELD_DEFS:
            common = common_values.get(f.key, "") if f.allow_common else ""
            values[f.key] = common or ask_from_user(f.question, f.options, mandatory=f.mandatory, is_date=f.is_date)

        # erikoistapaus: sampling / received date
        while True:
            sampling_date = ask_from_user("Enter Sampling-Date (YYYY-MM-DD):", is_date=True)
            received_date = ask_from_user("Enter Sample-Received-Date (YYYY-MM-DD):", is_date=True)
            if not sampling_date and not received_date:
                print("At least one of Sampling-Date or Sample-Received-Date is required.")
                continue

            break

        library = values["library"]
        lib_other = ask_from_user("Enter Library-Other:") if library == "Other" else ""
        add_results = ask_from_user("Add Results to DB? (y/n):", ["y", "n"]) or "n"

        meta = Metadata(
            identifier=sample_id,
            sampling_date=sampling_date,
            sample_received_date=received_date,
            file1=str(r1.resolve()),
            file2=str(r2.resolve()),
            library_other=lib_other,
            add_results=add_results,
            **values,   # species, rymy_id, food_bug, source, sampling_reason, owner, location, amr_phenotype, additional_information, accession, instrument, library
        )
        metadata_list.append(meta)
    if metadata_list:
        date_str = datetime.now().strftime("%Y%m%d")
        output_path = Path(sample_fastq_folder) / f"metadata_{date_str}.csv"
        Metadata.write_to_csv(str(output_path), metadata_list)
        print(f"\nWrote metadata for {len(metadata_list)} sample(s) to {output_path}")
    else:
        print("No valid samples with both R1 and R2 found. metadata.csv not written.")
if __name__ == '__main__':
    main()

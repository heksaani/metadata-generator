"""Python script to make the metadata template"""
from pathlib import Path
from collections import defaultdict
import csv, os


output_columns = ["#Pipeline-Species", "Primary-Identifier", "RYMY-ID", "Food_bug", "Source",
                                "Sampling-Reason", "Sampling-Date", "Sample-Received-Date",
                                "Owner-Collection", "Location", "AMR-Phenotype", "Additional-Information",
                                "File_1", "File_2", "Accession", "Instrument", "Library", "Library-Other", "Add-Results"]

questions = ["Enter Species: (mandatory)", 
             "Enter RYMY-ID:", "Enter Food_bug:", "Enter Source (e.g., Human):",
             "Enter Sampling-Reason:", "Enter Sampling-Date (YYYY-MM-DD):", "Enter Sample-Received-Date (YYYY-MM-DD):",
             "Enter Owner-Collection (your organization):", "Enter Location (e.g., Finland) this is case sensitive:",
             "Enter AMR-Phenotype:", "Enter Additional-Information:", "Enter Accession:", "Enter Instrument:",
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

class Metadata:
    def __init__(self, species:str, identifier:str, rymy_id:str, food_bug:str, source:str,
                 sampling_reason:str, sampling_date:str, sample_received_date:str,
                 owner:str, location:str, amr_phenotype:str, info:str, file1:str, file2:str,
                 accession:str, instrument:str, library:str, lib_other:str, add_results:str):
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
        self.additional_information = info
        self.file1 = file1
        self.file2 = file2
        self.accession = accession
        self.instrument = instrument
        self.library = library
        self.library_other = lib_other
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

        with open(filename, "w", newline='') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(output_columns)
                for meta in metadata_list:
                    writer.writerow(meta.to_list())

def create_sample_dictionary(sample_fastq_folder:str):

    """Function that returns dictionary that contains 
        sample_identifier: [fastq1,fastq2] from the given path and its subfolders """
    
    base_dir = Path(sample_fastq_folder)
    fastq_files = list(base_dir.rglob('*.fastq.gz'))
    if not fastq_files:
        print(f"-------- ERROR: No fastq.gz files found in the folder {sample_fastq_folder}")
        return {}

    sample_dict = defaultdict(lambda: [None, None])
    for file in fastq_files:
        filename = file.name
        file_path = file
        if '_R1' in filename:
            identifier = filename.split('_')[0]
            sample_dict[identifier][0] = file_path # type: ignore

        elif '_R2' in filename:
            identifier = filename.split('_')[0]
            sample_dict[identifier][1] = file_path # type: ignore
        else:
            print(f"-------- ERROR the file {file} name does not contain R1/R2")
    return sample_dict

def validate_input(user_input, valid_options: None ):
    "Check if the user input is valid for the pipeline"
    if user_input not in valid_options:
        print(f"Invalid input. Please choose from {valid_options}.")
        return False
    return True

def ask_from_user(question, valid_options, mandatory = False) -> str:
    if mandatory is True:
        user_input = str(input(question))
        if valid_options is not None and user_input in valid_options:
            return user_input
    

def main():

    print("This script works as follows :" \
    " ")



    sample_fastq_folder= input("Give the path to sample fastq files folder:")
    sample_dict = create_sample_dictionary(sample_fastq_folder) # this will create a dictionary with sample identifiers as keys and lists of fastq file paths as values
    metadata_list = [] # list to hold Metadata objects
    if not sample_dict:
        print("No samples found. Exiting.")
        return
    print("\n--- If you want to give same values to all samples ")
    
    
    # Kysytään globaalit/yhteiset tiedot ennen silmukkaa
    common_specie = ask_from_user("Common Species for all samples", valid_options=valid_species_names, mandatory=True)
    common_source = ask_from_user("Common Source for all samples", valid_options=valid_source, mandatory=True)
    common_owner = ask_from_user("Common Owner-Collection for all samples",  valid_options=valid_owner, mandatory=True)
    common_instrument = ask_from_user("Common Instrument for all samples", valid_options=valid_instruments, mandatory=True)


    for sample_id, sample_list in sample_dict.items(): # iterate over the dictionary items
        while True:
            print(f"For sample {sample_id} Input following metadata information (leave plank in case information is not available)")
            input_specie = common_specie if common_specie else ask_from_user("Enter Species: (compulsory feld, can't be empty)", valid_options=valid_species_names, mandatory=True)
            input_rymy_id = ask_from_user("Enter RYMY-ID:", valid_options=valid_species_names, mandatory=True)
            input_food_bug = ask_from_user("Enter Food_bug:",valid_options=valid_species_names, mandatory=True)
            input_source = common_source if common_source else ask_from_user("Enter Source (e.g., Human):", valid_options=valid_species_names, mandatory=True)
            input_sampling_reason = ask_from_user("Enter Sampling-Reason:", valid_options=valid_species_names, mandatory=True)
            input_sampling_date = ask_from_user("Enter Sampling-Date (YYYY-MM-DD):", valid_options=valid_species_names, mandatory=True)
            input_sample_received_date = ask_from_user("Enter Sample-Received-Date (YYYY-MM-DD):", valid_options=valid_species_names, mandatory=True)
            input_owner = ask_from_user("", valid_options=valid_owner, mandatory=
            input_location =ask_from_user()
            input_amr_pheno =  ask_from_user()
            input_info = ask_from_user()
            meta = Metadata(
                species=input_specie,
                identifier=sample_id,
                rymy_id=input_rymy_id,
                food_bug=input_food_bug,
                source=input_source,
                sampling_reason=input_sampling_reason,
                sampling_date=input_sampling_date,
                sample_received_date=input_sample_received_date,
                owner=input_owner,
                location=input_location,
                amr_phenotype=input_amr_pheno,
                info=input_info,
                file1=sample_list[0],
                file2=sample_list[1],
                accession = input_accession,
                instrument=input_instrument,
                library=input_library,
                lib_other=input_lib,
                add_results=input_add_results
            )
            metadata_list.append(meta)
    Metadata.write_to_csv("metadata.csv", metadata_list)       


# Column 5: Source (compulsory, set terms)
# Columns 7-8: Sampling-Date, Sample-Received-Date (conditionally optional)
# Column 9: Owner-Collection (compulsory, set terms)

if __name__ == '__main__':
    main()


ask_from_user(sample_id, "Enter Species:", specie)
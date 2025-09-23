"""Python script to make the metadata template"""
from pathlib import Path
from collections import defaultdict
import csv, os


class Metadata:
    def __init__(self, species:str, identifier:str, rymy_id:str, food_bug:str, source:str,
                 sampling_reason:str, sampling_date:str, sample_received_date:str, 
                 owner:str, location:str, amr_phenotype:str, info:str, file1:str, file2:str,
                 instrument:str, library:str, lib_other:str, add_results:str):
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
        self.instrument = instrument
        self.library = library
        self.library_other = lib_other
        self.add_results= add_results

    def to_list(self):
        """Returns the metadata as a list of fields for CSV writing"""
        return [self.species, self.identifier, self.rymy_id, self.food_bug, self.source,
                self.sampling_reason, self.sampling_date, self.sample_received_date,
                self.owner, self.location, self.amr_phenotype, self.additional_information,
                self.file1, self.file2, self.instrument, self.library, self.library_other,
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
                writer.writerow(["#Pipeline-Species", "Primary-Identifier", "RYMY-ID", "Food_bug", "Source",
                                "Sampling-Reason", "Sampling-Date", "Sample-Received-Date",
                                "Owner-Collection", "Location", "AMR-Phenotype", "Additional-Information",
                                "File_1", "File_2", "Instrument", "Library", "Library-Other", "Add-Results"])
                for meta in metadata_list:
                    writer.writerow(meta.to_list())

def input_with_default(prompt, default):
    user_input = input(f"{prompt} [{default}]: ")
    if user_input.strip() == "":
        return default
    return user_input

def ask_global_metadata():
    species = input_with_default("Enter #Pipeline-Species", "Escherichia coli")
    owner = input_with_default("Enter Owner-Collection (your organization): ", "THL")
    location = input_with_default("Enter Location (e.g., Finland) this is case sensitive: ", "Finland")
    add_results = input_with_default("Add Results to DB? (y/n): ", "y").lower()
    return species, owner, location, add_results

def ask_sample_metadata(sample_id):
    print(f"\nMetadata for sample {sample_id}:")
    source = input_with_default("Enter Source (e.g., Human):", "Human")
    sampling_date = input("Enter Sampling-Date (YYYY-MM-DD):")
    sample_received_date = ""
    if sampling_date:
        sample_received_date = input("Enter Sample-Received-Date (optional, press Enter to skip):")
    else:
        sample_received_date = input("Enter Sample-Received-Date (YYYY-MM-DD):")
    return source, sampling_date, sample_received_date

def is_sample_in_dict(identifier, sample_dict, file_path):
    """"""

    if identifier not in sample_dict.keys(): 
        sample_dict[identifier] = [file_path]
    else:
        sample_dict[identifier].append(file_path)

def create_sample_dictionary(sample_fastq_folder:str):

    """Function that returns dictionary that contains 
        sample_identifier: [fastq1,fastq2] from the given path and its subfolders """
    
    base_dir = Path(sample_fastq_folder)
    fastq_files = list(base_dir.rglob('*.fastq.gz'))

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


def main():
    species, owner, location, add_results = ask_global_metadata()
    sample_fastq_folder= input("Give the path to sample fastq files folder:")
    sample_dict = create_sample_dictionary(sample_fastq_folder)
    metadata_list = []
    for sample_id, sample_list in sample_dict.items():
        #source, sampling_date, sample_received_date = ask_sample_metadata(sample_id)
        source = "Human"
        sampling_date ="2024-04-02"
        sample_received_date = ""
        meta = Metadata(
            species=species,
            identifier=sample_id,
            rymy_id="",
            food_bug="",
            source=source,
            sampling_reason="",
            sampling_date=sampling_date,
            sample_received_date=sample_received_date,
            owner=owner,
            location=location,
            amr_phenotype="",
            info="",
            file1=sample_list[0], # type: ignore
            file2=sample_list[1], # type: ignore
            instrument="",
            library="",
            lib_other="",
            add_results=add_results
        )
        metadata_list.append(meta)
        Metadata.write_to_csv("metadata.csv", metadata_list)


if __name__ == '__main__':
    main()

## TODO add check that both R1 and R2 are infact in the csv 
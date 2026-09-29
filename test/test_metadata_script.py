"""
Pytest-testit metadata_script.py:lle.

Aja: pytest test_metadata_script.py -v

Oletus: testattava koodi on tiedostossa metadata_script.py samassa kansiossa.
Jos moduulisi nimi on eri, muuta alla oleva import-rivi vastaavaksi.
"""
import csv
import builtins
from pathlib import Path
from unittest.mock import patch

import pytest

import metadata_generator as ms


# ---------------------------------------------------------------------------
# validate_input
# ---------------------------------------------------------------------------

def test_validate_input_valid_value():
    assert ms.validate_input("Human", ms.valid_source) is True


def test_validate_input_invalid_value(capsys):
    assert ms.validate_input("Alien", ms.valid_source) is False
    captured = capsys.readouterr()
    assert "Invalid input" in captured.out


def test_validate_input_no_options_means_anything_goes():
    assert ms.validate_input("anything at all", None) is True
    assert ms.validate_input("", None) is True


# ---------------------------------------------------------------------------
# validate_date
# ---------------------------------------------------------------------------

def test_validate_date_valid():
    assert ms.validate_date("2023-11-08") is True


@pytest.mark.parametrize("bad_value", [
    "08-11-2023",       # väärä järjestys
    "2023/11/08",        # väärä erotin
    "2023-13-40",        # ei ole olemassa oleva päivämäärä
    "not a date",
    "",
])
def test_validate_date_invalid(bad_value):
    assert ms.validate_date(bad_value) is False


# ---------------------------------------------------------------------------
# ask_from_user (input() mockattu)
# ---------------------------------------------------------------------------

def test_ask_from_user_optional_empty_returns_empty_string():
    with patch("builtins.input", return_value=""):
        result = ms.ask_from_user("Enter Food_bug:", mandatory=False)
    assert result == ""


def test_ask_from_user_mandatory_empty_then_valid():
    # Ensimmäinen vastaus tyhjä (hylätään), toinen kelvollinen
    answers = iter(["", "Human"])
    with patch("builtins.input", lambda _q: next(answers)):
        result = ms.ask_from_user("Enter Source:", ms.valid_source, mandatory=True)
    assert result == "Human"


def test_ask_from_user_rejects_invalid_option_then_accepts_valid():
    answers = iter(["Ecoli-typo", "Escherichia coli"])
    with patch("builtins.input", lambda _q: next(answers)):
        result = ms.ask_from_user("Enter Species:", ms.valid_species_names, mandatory=True)
    assert result == "Escherichia coli"


def test_ask_from_user_date_field_rejects_bad_date():
    answers = iter(["not-a-date", "2023-11-08"])
    with patch("builtins.input", lambda _q: next(answers)):
        result = ms.ask_from_user("Enter Sampling-Date:", is_date=True)
    assert result == "2023-11-08"


def test_ask_from_user_optional_date_empty_is_ok():
    with patch("builtins.input", return_value=""):
        result = ms.ask_from_user("Enter Sample-Received-Date:", is_date=True, mandatory=False)
    assert result == ""


# ---------------------------------------------------------------------------
# create_sample_dictionary
# ---------------------------------------------------------------------------

def test_create_sample_dictionary_empty_folder(tmp_path, capsys):
    result = ms.create_sample_dictionary(str(tmp_path))
    assert result == {}
    captured = capsys.readouterr()
    assert "No fastq.gz files found" in captured.out


def test_create_sample_dictionary_finds_pairs(tmp_path):
    (tmp_path / "SAMPLE1_R1.fastq.gz").touch()
    (tmp_path / "SAMPLE1_R2.fastq.gz").touch()
    (tmp_path / "SAMPLE2_R1.fastq.gz").touch()
    (tmp_path / "SAMPLE2_R2.fastq.gz").touch()

    result = ms.create_sample_dictionary(str(tmp_path))

    assert set(result.keys()) == {"SAMPLE1", "SAMPLE2"}
    assert result["SAMPLE1"][0].name == "SAMPLE1_R1.fastq.gz"
    assert result["SAMPLE1"][1].name == "SAMPLE1_R2.fastq.gz"


def test_create_sample_dictionary_missing_r2(tmp_path):
    (tmp_path / "SAMPLE1_R1.fastq.gz").touch()
    # R2 puuttuu tarkoituksella

    result = ms.create_sample_dictionary(str(tmp_path))

    assert result["SAMPLE1"][0] is not None
    assert result["SAMPLE1"][1] is None


def test_create_sample_dictionary_file_without_r1_r2_marker(tmp_path, capsys):
    (tmp_path / "weird_name.fastq.gz").touch()

    result = ms.create_sample_dictionary(str(tmp_path))

    captured = capsys.readouterr()
    assert "does not contain R1/R2" in captured.out
    # Tiedostoa ei liitetä mihinkään näytteeseen
    assert all(v == [None, None] for v in result.values()) or result == {}


def test_create_sample_dictionary_searches_subfolders(tmp_path):
    subfolder = tmp_path / "batch1"
    subfolder.mkdir()
    (subfolder / "SAMPLE1_R1.fastq.gz").touch()
    (subfolder / "SAMPLE1_R2.fastq.gz").touch()

    result = ms.create_sample_dictionary(str(tmp_path))

    assert "SAMPLE1" in result


# ---------------------------------------------------------------------------
# Metadata: to_list, header_exists, write_to_csv
# ---------------------------------------------------------------------------

def make_sample_metadata(**overrides):
    defaults = dict(
        species="Escherichia coli", identifier="SAMPLE1", rymy_id="", food_bug="",
        source="Human", sampling_reason="", sampling_date="2023-11-08",
        sample_received_date="", owner="THL", location="Finland",
        amr_phenotype="", additional_information="", file1="f1.fastq.gz",
        file2="f2.fastq.gz", accession="", instrument="Illumina MiSeq",
        library="Nextera XT", library_other="", add_results="n",
    )
    defaults.update(overrides)
    return ms.Metadata(**defaults)


def test_metadata_to_list_order_matches_output_columns():
    meta = make_sample_metadata()
    row = meta.to_list()
    assert len(row) == len(ms.output_columns)
    assert row[0] == "Escherichia coli"   # #Pipeline-Species
    assert row[1] == "SAMPLE1"            # Primary-Identifier
    assert row[-1] == "n"                 # Add-Results


def test_metadata_library_other_empty_when_library_not_other():
    meta = make_sample_metadata(library="Nextera XT", library_other="")
    assert meta.library_other == ""


def test_header_exists_missing_file(tmp_path):
    missing = tmp_path / "does_not_exist.csv"
    assert ms.Metadata.header_exists(str(missing)) is False


def test_header_exists_wrong_header(tmp_path):
    f = tmp_path / "metadata.csv"
    f.write_text("something;else;here\n")
    assert ms.Metadata.header_exists(str(f)) is False


def test_header_exists_correct_header(tmp_path):
    f = tmp_path / "metadata.csv"
    f.write_text("#Pipeline-Species;Primary-Identifier;...\n")
    assert ms.Metadata.header_exists(str(f)) is True


def test_write_to_csv_writes_header_and_rows(tmp_path):
    out_file = tmp_path / "metadata.csv"
    meta1 = make_sample_metadata(identifier="SAMPLE1")
    meta2 = make_sample_metadata(identifier="SAMPLE2")

    ms.Metadata.write_to_csv(str(out_file), [meta1, meta2])

    assert out_file.exists()
    with open(out_file, newline="") as f:
        reader = list(csv.reader(f, delimiter=";"))

    assert reader[0] == ms.output_columns
    assert reader[1][1] == "SAMPLE1"
    assert reader[2][1] == "SAMPLE2"
    assert len(reader) == 3  # header + 2 riviä


# ---------------------------------------------------------------------------
# Integraatiotesti: main() päästä päähän
#
# HUOM: nämä kaksi testiä olettavat, että main()-funktioon on lisätty
# write_to_csv-kutsu (katso "1. write_to_csv-kutsu puuttuu" yllä) sekä
# tyhjän/virheellisen polun tarkistus (katso "2. Tyhjä polku" yllä).
# Jos et ole vielä tehnyt näitä korjauksia, nämä kaksi testiä epäonnistuvat.
# ---------------------------------------------------------------------------

def _build_answers(sample_fastq_folder):
    """Rakentaa input()-vastausjonon yhdelle näytteelle (SAMPLE1),
    ilman yhteisiä (common) arvoja, ja jättää viimeisen kysymyksen tyhjäksi
    -- juuri se tapaus, joka aiemmin aiheutti TypeError-virheen."""
    return [
        sample_fastq_folder,          # kansiopolku
        "",                            # common species -> tyhjä
        "",                            # common source -> tyhjä
        "",                            # common owner -> tyhjä
        "",                            # common instrument -> tyhjä
        "Escherichia coli",           # species
        "",                            # rymy_id
        "",                            # food_bug
        "Human",                       # source
        "",                            # sampling_reason
        "THL",                         # owner
        "Finland",                     # location
        "",                            # amr_phenotype
        "",                            # additional_information
        "",                            # accession
        "Illumina MiSeq",             # instrument
        "Nextera XT",                 # library
        "2023-11-08",                 # sampling_date
        "",                            # received_date (jätetään tyhjäksi, koska sampling_date annettu)
        "",                            # Add Results -> TYHJÄ (aiempi bugi)
    ]


def test_main_end_to_end_writes_expected_csv(tmp_path, monkeypatch):
    fastq_dir = tmp_path / "data"
    fastq_dir.mkdir()
    (fastq_dir / "SAMPLE1_R1.fastq.gz").touch()
    (fastq_dir / "SAMPLE1_R2.fastq.gz").touch()

    answers = iter(_build_answers(str(fastq_dir)))
    monkeypatch.setattr(builtins, "input", lambda *_args: next(answers))

    ms.main()

    out_file = fastq_dir / "metadata.csv"
    assert out_file.exists(), "metadata.csv ei syntynyt -- write_to_csv-kutsu puuttuu main()-funktiosta?"

    with open(out_file, newline="") as f:
        rows = list(csv.reader(f, delimiter=";"))

    assert rows[0] == ms.output_columns
    assert len(rows) == 2  # otsikko + 1 näyte

    row = dict(zip(ms.output_columns, rows[1]))
    assert row["#Pipeline-Species"] == "Escherichia coli"
    assert row["Primary-Identifier"] == "SAMPLE1"
    assert row["Sampling-Date"] == "2023-11-08"
    assert row["Sample-Received-Date"] == ""
    assert row["Add-Results"] == "n"   # tyhjä syöte -> oletusarvo "n"
    assert row["Library-Other"] == ""  # Library != "Other" -> tyhjä


def test_main_rejects_empty_folder_path(tmp_path, monkeypatch, capsys):
    fastq_dir = tmp_path / "data"
    fastq_dir.mkdir()
    (fastq_dir / "SAMPLE1_R1.fastq.gz").touch()
    (fastq_dir / "SAMPLE1_R2.fastq.gz").touch()

    # Ensin annetaan tyhjä polku, sitten kelvollinen -- loput vastaukset kuten yllä
    answers = iter([""] + _build_answers(str(fastq_dir)))
    monkeypatch.setattr(builtins, "input", lambda *_args: next(answers))

    ms.main()

    captured = capsys.readouterr()
    assert "cannot be empty" in captured.out or "not a valid directory" in captured.out


def test_main_skips_sample_missing_r2(tmp_path, monkeypatch):
    fastq_dir = tmp_path / "data"
    fastq_dir.mkdir()
    # SAMPLE1: vain R1, ei R2 -- pitäisi ohittaa kokonaan
    (fastq_dir / "SAMPLE1_R1.fastq.gz").touch()
    # SAMPLE2: molemmat tiedostot löytyvät
    (fastq_dir / "SAMPLE2_R1.fastq.gz").touch()
    (fastq_dir / "SAMPLE2_R2.fastq.gz").touch()

    answers = iter(_build_answers(str(fastq_dir)))
    # _build_answers antaa vastaukset vain yhdelle näytteelle (SAMPLE2:lle,
    # koska SAMPLE1 ohitetaan eikä kysy mitään sille)
    monkeypatch.setattr(builtins, "input", lambda *_args: next(answers))

    ms.main()

    out_file = fastq_dir / "metadata.csv"
    with open(out_file, newline="") as f:
        rows = list(csv.reader(f, delimiter=";"))

    identifiers = [row[1] for row in rows[1:]]
    assert "SAMPLE1" not in identifiers
    assert "SAMPLE2" in identifiers

""" Reindex the native ID of mzML files to make them unique across multiple
mzML files (fractions). """
import argparse
import re
from pathlib import Path
from typing import Dict
from pyopenms import MzMLFile, MSExperiment, SourceFile


SCAN_NATIVE_ID_TYPE = 'scan number only nativeID format'
SCAN_NATIVE_ID_ACCESSION = 'MS:1000776'
THERMO_NATIVE_ID_TYPE = 'Thermo nativeID format'
THERMO_NATIVE_ID_ACCESSION = 'MS:1000768'
THERMO_NATIVE_ID = re.compile(r'controllerType=(\d+) controllerNumber=(\d+) scan=\d+')


def set_native_id_format(source_file, thermo):
    """Describe the native ID syntax written into the reindexed mzML."""
    source_file.setNativeIDType(THERMO_NATIVE_ID_TYPE if thermo else SCAN_NATIVE_ID_TYPE)
    source_file.setNativeIDTypeAccession(
        THERMO_NATIVE_ID_ACCESSION if thermo else SCAN_NATIVE_ID_ACCESSION
    )
    return source_file


def parse_args():
    """ parse args """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input-path',
        type=str,
        nargs='*',
        help='Path to the input mzML file to be reindexed.',
        required=True
    )
    parser.add_argument(
        '--output-prefix',
        type=str,
        help='Output prefix.',
        required=True
    )
    parser.add_argument(
        '--keep-all-metadata',
        action='store_true',
        help='Keeps all metadata, instrumental data, chromatogram, and sample '
        'data'
    )
    return parser.parse_args()


def main():
    """ main """
    args = parse_args()

    # When set, all metadata, instrumental data, chromatogram, and sample data
    # will be saved. They are usually not essential for downstream analysis.
    keep_all_metadata:bool = args.keep_all_metadata

    next_scan_number = 1
    native_id_map:Dict[str,str] = {}
    for file_ind, input_path in enumerate(args.input_path):
        exp = MSExperiment()
        MzMLFile().load(input_path, exp)
        if keep_all_metadata:
            exp_new = MSExperiment(exp)
            exp_new.clear(False)
        else:
            exp_new = MSExperiment()
        native_id_map.clear()

        if exp.metaValueExists('mzml_id'):
            mzml_id = exp.getMetaValue('mzml_id')
        else:
            mzml_id = Path(input_path).stem

        thermo_ids = all(THERMO_NATIVE_ID.fullmatch(spectrum.getNativeID()) for spectrum in exp)

        source_files = exp.getSourceFiles()
        if not source_files:
            source_file = SourceFile()
            source_file.setNameOfFile(Path(input_path).name)
            source_file.setPathToFile(str(Path(input_path).parent))
            source_files = [source_file]
        source_files = [set_native_id_format(source_file, thermo_ids) for source_file in source_files]

        for spectrum in exp:
            raw_id = spectrum.getNativeID()
            if thermo_ids:
                match = THERMO_NATIVE_ID.fullmatch(raw_id)
                new_id = (f"controllerType={match.group(1)} "
                          f"controllerNumber={match.group(2)} scan={next_scan_number}")
            else:
                new_id = f"scan={next_scan_number}"
            native_id_map[raw_id] = new_id
            spectrum.setNativeID(new_id)
            spectrum_source_file = spectrum.getSourceFile()
            if spectrum_source_file.getNameOfFile() or spectrum_source_file.getPathToFile():
                spectrum.setSourceFile(set_native_id_format(spectrum_source_file, thermo_ids))

            ms_level = spectrum.getMSLevel()
            spectrum_title = f"{mzml_id}.{next_scan_number}.{next_scan_number}."
            if ms_level > 1:
                spectrum_title = f"{spectrum_title}{ms_level}"

            spectrum.setMetaValue('spectrum title', spectrum_title)

            # Also fix the spectrum reference of precursors.
            if ms_level > 1:
                precursors_fixed = []
                for precursor in spectrum.getPrecursors():
                    # Apparently not all precursors have spectrum reference..
                    # If they don't, there is nothing we should worry about.
                    if precursor.metaValueExists('spectrum_ref'):
                        precursor_scan_id = precursor.getMetaValue('spectrum_ref')
                        precursor_ref_id = native_id_map[precursor_scan_id]
                        precursor.setMetaValue('spectrum_ref', precursor_ref_id)

                    precursors_fixed.append(precursor)
                spectrum.setPrecursors(precursors_fixed)

            exp_new.addSpectrum(spectrum)
            next_scan_number += 1

        # Copy experimental settings.
        exp_new.setSourceFiles(source_files)
        if keep_all_metadata:
            exp_new.setHPLC(exp.getHPLC())
            exp_new.setInstrument(exp.getInstrument())
            exp_new.setChromatograms(exp.getChromatograms())
            exp_new.setSample(exp.getSample())

        output_path = f"{args.output_prefix}_{file_ind + 1}.mzML"
        MzMLFile().store(output_path, exp_new)

if __name__ == '__main__':
    main()

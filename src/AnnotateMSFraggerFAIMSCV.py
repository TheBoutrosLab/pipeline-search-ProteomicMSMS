"""Add missing spectrum-derived UserParams to MSFragger peptide IDs.

Currently only FAIMS_CV is transferred from mzML to idXML. Spectrum peak arrays
are not loaded, and non-FAIMS idXML is copied without rewriting it.
"""
# pylint: disable=no-name-in-module

import argparse
import math
import shutil

import pyopenms
from pyopenms import DriftTimeUnit, IdXMLFile, MSExperiment, MSSpectrum, MzMLFile, PeakFileOptions


class PSMSpectrumAnnotator:
    """Match peptide identifications to source spectra and annotate missing fields."""

    def __init__(self, idxml_path, mzml_path):
        self.idxml_path = idxml_path
        self.mzml_path = mzml_path
        self.protein_ids = []
        self.peptide_ids = (pyopenms.PeptideIdentificationList()
                            if hasattr(pyopenms, "PeptideIdentificationList") else [])
        self.experiment = MSExperiment()
        self.spectra_by_id: dict[str, MSSpectrum] = {}
        self.duplicate_ids = set()
        self.faims_cv_by_id = {}
        self.has_faims = False
        self.loaded = False

    def load(self):
        """Read identification and spectrum metadata, then build the native ID index."""
        self.protein_ids = []
        self.peptide_ids = (pyopenms.PeptideIdentificationList()
                            if hasattr(pyopenms, "PeptideIdentificationList") else [])
        IdXMLFile().load(self.idxml_path, self.protein_ids, self.peptide_ids)

        options = PeakFileOptions()
        options.setFillData(False)
        mzml = MzMLFile()
        mzml.setOptions(options)
        self.experiment = MSExperiment()
        mzml.load(self.mzml_path, self.experiment)

        self.spectra_by_id = {}
        self.duplicate_ids = set()
        self.faims_cv_by_id = {}
        self.has_faims = False
        self.index_spectra()
        self.loaded = True

    @staticmethod
    def as_text(value):
        """Normalize pyOpenMS string values across binding versions."""
        return value.decode("utf-8") if isinstance(value, bytes) else str(value)

    def index_spectra(self):
        """Index spectra by native ID and track explicit or inherited FAIMS CV."""
        last_voltage = None
        for spectrum in self.experiment:
            native_id = self.as_text(spectrum.getNativeID())
            if not native_id:
                raise ValueError(f"mzML spectrum in {self.mzml_path} has no native ID")
            if native_id in self.spectra_by_id:
                self.duplicate_ids.add(native_id)
            self.spectra_by_id[native_id] = spectrum

            if spectrum.getDriftTimeUnit() == DriftTimeUnit.FAIMS_COMPENSATION_VOLTAGE:
                self.has_faims = True
                voltage = float(spectrum.getDriftTime())
                if not math.isfinite(voltage):
                    raise ValueError(f"Invalid FAIMS voltage on spectrum {native_id!r}")
                last_voltage = voltage
            elif spectrum.getMSLevel() > 1:
                voltage = last_voltage
            else:
                voltage = None
            self.faims_cv_by_id[native_id] = voltage

    def resolve_spectrum(self, peptide):
        """Find the unique spectrum identified by a peptide's native reference."""
        reference = (self.as_text(peptide.getMetaValue("spectrum_reference"))
                     if peptide.metaValueExists("spectrum_reference") else "")
        if not reference:
            raise ValueError(
                f"Peptide identification in {self.idxml_path} has no spectrum_reference"
            )
        if reference in self.duplicate_ids:
            raise ValueError(f"Ambiguous spectrum_reference {reference!r} in {self.mzml_path}")
        try:
            return reference, self.spectra_by_id[reference]
        except KeyError as error:
            raise ValueError(
                f"Unresolved spectrum_reference {reference!r} in {self.mzml_path}"
            ) from error

    def annotate_faims_cv(self, peptide, reference, spectrum):
        """Write or verify the FAIMS_CV UserParam for one matched spectrum."""
        if spectrum.getMSLevel() < 2:
            raise ValueError(f"Identification references non-MS2 spectrum {reference!r}")
        voltage = self.faims_cv_by_id[reference]
        if voltage is None:
            raise ValueError(
                f"No FAIMS voltage for spectrum_reference {reference!r} in {self.mzml_path}"
            )
        if peptide.metaValueExists("FAIMS_CV"):
            existing = float(peptide.getMetaValue("FAIMS_CV"))
            if not math.isfinite(existing) or not math.isclose(existing, voltage, abs_tol=1e-6):
                raise ValueError(
                    f"FAIMS_CV mismatch for {reference!r}: idXML={existing}, mzML={voltage}"
                )
            return False
        peptide.setMetaValue("FAIMS_CV", voltage)
        return True

    def annotate(self, output_path):
        """Annotate every FAIMS PSM, then write a valid idXML."""
        if not self.loaded:
            raise RuntimeError("Call load() before annotate()")
        if not self.has_faims:
            shutil.copyfile(self.idxml_path, output_path)
            return 0

        added = 0
        for index, peptide in enumerate(self.peptide_ids):
            reference, spectrum = self.resolve_spectrum(peptide)
            changed = self.annotate_faims_cv(peptide, reference, spectrum)
            if changed:
                self.peptide_ids[index] = peptide
                added += 1
        IdXMLFile().store(output_path, self.protein_ids, self.peptide_ids)
        return added


def main():
    """Run the annotation for one MSFragger fraction."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-mzml", required=True)
    parser.add_argument("--input-idxml", required=True)
    parser.add_argument("--output-idxml", required=True)
    args = parser.parse_args()
    annotator = PSMSpectrumAnnotator(args.input_idxml, args.input_mzml)
    annotator.load()
    added = annotator.annotate(args.output_idxml)
    print(f"Added FAIMS_CV to {added} peptide identifications")


if __name__ == "__main__":
    main()

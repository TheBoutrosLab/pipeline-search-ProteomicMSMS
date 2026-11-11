"""Restore mzML native spectrum references in MSFraggerAdapter idXML output.

Some pepXML imports retain ``scan=<start_scan>`` instead of the mzML native ID.
MSFragger records that native ID on each ``spectrum_query`` element.
"""
# pylint: disable=no-name-in-module

import argparse
import xml.etree.ElementTree as ET

import pyopenms
from pyopenms import IdXMLFile


NATIVE_ID_ATTRIBUTES = ("SpectrumNativeId", "spectrumNativeID", "native_id")


def scan_to_native_id(pepxml_path):
    """Return the per-file scan reference to native ID mapping from pepXML."""
    mapping = {}
    for _, element in ET.iterparse(pepxml_path, events=("end",)):
        if element.tag.rsplit("}", 1)[-1] != "spectrum_query":
            continue

        scan = element.attrib.get("start_scan")
        native_id = next(
            (element.attrib[name] for name in NATIVE_ID_ATTRIBUTES
             if element.attrib.get(name)),
            None,
        )
        if scan is None or native_id is None:
            raise ValueError(
                "MSFragger pepXML spectrum_query lacks start_scan or a native ID "
                f"attribute ({', '.join(NATIVE_ID_ATTRIBUTES)})"
            )

        scan_ref = f"scan={scan}"
        if scan_ref in mapping and mapping[scan_ref] != native_id:
            raise ValueError(f"Ambiguous native IDs for {scan_ref} in {pepxml_path}")
        mapping[scan_ref] = native_id
        element.clear()
    return mapping


def main():
    """Replace idXML scan references using the matching pepXML native IDs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-path", required=True)
    parser.add_argument("--input-pepxml", required=True)
    parser.add_argument("--output-path", required=True)
    args = parser.parse_args()

    protein_ids = []
    peptide_ids = (pyopenms.PeptideIdentificationList()
                   if hasattr(pyopenms, "PeptideIdentificationList") else [])
    IdXMLFile().load(args.input_path, protein_ids, peptide_ids)
    mapping = scan_to_native_id(args.input_pepxml)
    native_ids = set(mapping.values())

    for index, peptide in enumerate(peptide_ids):
        if not peptide.metaValueExists("spectrum_reference"):
            raise ValueError("Peptide identification has no spectrum_reference")
        reference = peptide.getMetaValue("spectrum_reference")
        if isinstance(reference, bytes):
            reference = reference.decode("utf-8")
        if reference in mapping:
            peptide.setMetaValue("spectrum_reference", mapping[reference])
            peptide_ids[index] = peptide
        elif reference not in native_ids:
            raise ValueError(f"Cannot resolve spectrum_reference {reference!r}")

    IdXMLFile().store(args.output_path, protein_ids, peptide_ids)


if __name__ == "__main__":
    main()

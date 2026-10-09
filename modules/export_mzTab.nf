/** Export all reported PSMs in merged idXML to mzTab. */
process export_mzTab {
    container params.docker_image_openms
    publishDir params.final_output_dir, mode: 'copy', pattern: '*.mzTab'

    input:
        path idxml_file
    output:
        path mztab_file
    script:
        mztab_file = "${idxml_file.baseName}.mzTab"
        def all_psms = params.export_all_psms ? '-export_all_psms' : ''
        """
        set -euo pipefail
        MzTabExporter -in ${idxml_file} -out ${mztab_file} ${all_psms}
        """
}

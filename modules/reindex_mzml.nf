/** Assign unique native spectrum IDs across the fractions of each sample. */
process reindex_mzml {
    container params.docker_image_pyopenms
    publishDir "${params.results_root_dir}/${sample}/OpenMS-${params.openms_version}/output/reindex_mzml", mode: 'copy', pattern: '*.mzML'

    input:
        tuple val(sample), path(input_mzMLs)
        path script_file
    output:
        tuple val(sample), path('*.mzML')
    script:
        def keep_metadata = params.reindex_mzml_keep_all_metadata ? '--keep-all-metadata' : ''
        """
        set -euo pipefail
        python ${script_file} --input-path ${input_mzMLs.join(' ')} \\
          --output-prefix ${sample}_reindex ${keep_metadata}
        """
}

/** Assign unique native spectrum IDs across all fractions of one sample. */
process reindex_mzml {
    container params.docker_image_pyopenms
    publishDir "${params.final_output_dir}/reindex_mzml", mode: 'copy', pattern: '*.mzML'

    input:
        path input_mzMLs
        path script_file
    output:
        path '*.mzML'
    script:
        def keep_metadata = params.reindex_mzml_keep_all_metadata ? '--keep-all-metadata' : ''
        """
        set -euo pipefail
        python ${script_file} --input-path ${input_mzMLs.join(' ')} \\
          --output-prefix ${params.sample_name}_reindex ${keep_metadata}
        """
}

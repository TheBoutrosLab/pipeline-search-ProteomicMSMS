/**
* Nextflow module to merge multiple mzML files into one.
*
* FileMerger documentation: https://abibuilder.informatik.uni-tuebingen.de/archive/openms/
* Documentation/nightly/html/TOPP_FileMerger.html
*
*/

process merge_mzML_OpenMS {
    container params.docker_image_openms

    publishDir "${params.final_output_dir}",
        mode: 'copy',
        pattern: "*.mzML"

    publishDir "${params.process_log_dir}/${task.process.replace(':', '/')}-${task.index}/",
        mode: 'copy',
        pattern: '.command.*',
        saveAs: { "log${file(it).name}" }

    input:
        file mzml_files

    output:
        file merged_mzml
        file ".command.*"

    script:
    merged_mzml = "${params.sample_name}_merged.mzML"
    """
    FileMerger \\
        -in ${mzml_files} \\
        -out ${merged_mzml} \\
        -threads ${task.cpus}
    """
}

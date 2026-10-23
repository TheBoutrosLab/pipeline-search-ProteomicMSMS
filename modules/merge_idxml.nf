/** Merge fraction idXML files for one search engine. */
process merge_idxml {
    container params.docker_image_openms
    publishDir "${params.results_root_dir}/${sample}/OpenMS-${params.openms_version}/output", mode: 'copy', pattern: '*.idXML'

    input:
        tuple val(sample), path(idxml_files)
        val search_engine
    output:
        tuple val(sample), path(merged_idxml)
    script:
        merged_idxml = "${sample}_${search_engine}.idXML"
        def merge_option = params.merge_proteins_add_PSMs ? '-merge_proteins_add_PSMs' : ''
        """
        set -euo pipefail
        IDMerger -in ${idxml_files.sort { it.name }.join(' ')} -out ${merged_idxml} \\
          -threads ${task.cpus} ${merge_option}
        """
}

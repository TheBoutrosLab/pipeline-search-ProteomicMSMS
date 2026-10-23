/** OpenMS MSFraggerAdapter search, optional spectrum reference repair, and merge. */
import groovy.json.JsonOutput
include { generateAdapterConfig } from "${moduleDir}/common"
include { merge_idxml } from "${moduleDir}/merge_idxml"
include { export_mzTab } from "${moduleDir}/export_mzTab"

process create_json_MSFragger {
    output:
        path config_json
    exec:
        config_json = file("${task.workDir}/MSFraggerAdapter.json")
        config_json.write(JsonOutput.prettyPrint(JsonOutput.toJson(generateAdapterConfig('MSFraggerAdapter'))))
}

process create_ini_MSFragger {
    container params.docker_image_pyopenms
    publishDir "${params.results_root_dir}/intermediate/MSFragger", mode: 'copy', pattern: '*.ini', enabled: params.save_intermediate_files
    input:
        path config_json
        path script_file
    output:
        path 'MSFraggerAdapter.ini'
    script:
        """
        set -euo pipefail
        python ${script_file} ${config_json} MSFraggerAdapter.ini
        """
}

process search_database_MSFragger {
    container params.docker_image_openms
    publishDir "${params.results_root_dir}/${sample}/OpenMS-${params.openms_version}/output/per_fraction/MSFragger", mode: 'copy', pattern: '*.{idXML,pepXML}'
    input:
        tuple val(sample), path(mzml)
        path db
        path ini
        path executable
    output:
        tuple val(sample), path(output_idxml), path(output_pepxml)
    script:
        output_idxml = "${mzml.baseName}_MSFragger.idXML"
        output_pepxml = "${mzml.baseName}_MSFragger.pepXML"
        def heap = Math.max(1024, (task.memory.toMega() * 0.8) as int)
        """
        set -euo pipefail
        MSFraggerAdapter -in \$(pwd)/${mzml} -out ${output_idxml} \\
          -opt_out ${output_pepxml} -threads ${task.cpus} \\
          -database \$(pwd)/${db} -executable \$(pwd)/${executable} \\
          -java_heapmemory ${heap} -force -ini ${ini}
        """
}

/** Repair affected OpenMS versions' idXML spectrum references using pepXML. */
process fix_msfragger_spectrum_refs {
    container params.docker_image_pyopenms
    publishDir "${params.results_root_dir}/${sample}/OpenMS-${params.openms_version}/intermediate/MSFragger", mode: 'copy', pattern: '*.idXML', enabled: params.save_intermediate_files
    input:
        tuple val(sample), path(input_idxml), path(input_pepxml)
        path script_file
    output:
        tuple val(sample), path(output_idxml)
    script:
        output_idxml = "${input_idxml.baseName}_fixedSpectrumRefs.idXML"
        """
        set -euo pipefail
        python ${script_file} --input-path ${input_idxml} \\
          --input-pepxml ${input_pepxml} --output-path ${output_idxml}
        """
}

workflow workflow_search_database_MSFragger {
    take:
        mzml_file
    main:
        create_json_MSFragger()
        create_ini_MSFragger(create_json_MSFragger.out, file("${projectDir}/src/create_openms_ini.py"))
        search_database_MSFragger(mzml_file, file(params.decoy_database), create_ini_MSFragger.out, file(params.msfragger_executable))
        if (params.fix_msfragger_spectrum_refs) {
            fix_msfragger_spectrum_refs(search_database_MSFragger.out, file("${projectDir}/src/FixMSFraggerSpectrumRefs.py"))
            idxml = fix_msfragger_spectrum_refs.out
        } else {
            idxml = search_database_MSFragger.out.map { sample, id, pep -> tuple(sample, id) }
        }
        merge_idxml(idxml.groupTuple(), 'MSFragger')
        if (params.export_mzTab) export_mzTab(merge_idxml.out)
}

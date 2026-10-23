/** OpenMS SageAdapter search, then fraction merge and optional mzTab export. */
import groovy.json.JsonOutput
include { generateAdapterConfig } from "${moduleDir}/common"
include { merge_idxml } from "${moduleDir}/merge_idxml"
include { export_mzTab } from "${moduleDir}/export_mzTab"

process create_json_Sage {
    output:
        path config_json
    exec:
        config_json = file("${task.workDir}/SageAdapter.json")
        config_json.write(JsonOutput.prettyPrint(JsonOutput.toJson(generateAdapterConfig('SageAdapter'))))
}

process create_ini_Sage {
    container params.docker_image_pyopenms
    publishDir "${params.results_root_dir}/intermediate/Sage", mode: 'copy', pattern: '*.ini', enabled: params.save_intermediate_files
    input:
        path config_json
        path script_file
    output:
        path 'SageAdapter.ini'
    script:
        """
        set -euo pipefail
        python ${script_file} ${config_json} SageAdapter.ini
        """
}

process search_database_Sage {
    container params.docker_image_openms
    publishDir "${params.results_root_dir}/${sample}/OpenMS-${params.openms_version}/output/per_fraction/Sage", mode: 'copy', pattern: '*.idXML'
    input:
        tuple val(sample), path(mzml)
        path db, name: 'database.fasta'
        path ini
    output:
        tuple val(sample), path(output_idxml)
    script:
        output_idxml = "${mzml.baseName}_Sage.idXML"
        """
        set -euo pipefail
        SageAdapter -in ${mzml} -out ${output_idxml} -threads ${task.cpus} \\
          -database ${db} -sage_executable sage -ini ${ini}
        """
}

workflow workflow_search_database_Sage {
    take:
        mzml_file
    main:
        create_json_Sage()
        create_ini_Sage(create_json_Sage.out, file("${projectDir}/src/create_openms_ini.py"))
        search_database_Sage(mzml_file, file(params.decoy_database), create_ini_Sage.out)
        merge_idxml(search_database_Sage.out.groupTuple(), 'Sage')
        if (params.export_mzTab) export_mzTab(merge_idxml.out)
}

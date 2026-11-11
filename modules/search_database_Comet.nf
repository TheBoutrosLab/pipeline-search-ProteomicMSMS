/** OpenMS CometAdapter search, then fraction merge and optional mzTab export. */
import groovy.json.JsonOutput
include { generateAdapterConfig } from "${moduleDir}/common"
include { merge_idxml } from "${moduleDir}/merge_idxml"
include { export_mzTab } from "${moduleDir}/export_mzTab"

process create_json_Comet {
    output:
        path config_json
    exec:
        config_json = file("${task.workDir}/CometAdapter.json")
        config_json.write(JsonOutput.prettyPrint(JsonOutput.toJson(generateAdapterConfig('CometAdapter'))))
}

process create_ini_Comet {
    containerOptions params.project_script_mount_options
    container params.docker_image_pyopenms
    publishDir "${params.results_root_dir}/intermediate/Comet", mode: 'copy', pattern: '*.ini', enabled: params.save_intermediate_files
    input:
        path config_json
    output:
        path 'CometAdapter.ini'
    script:
        """
        set -euo pipefail
        python ${projectDir}/src/create_openms_ini.py ${config_json} CometAdapter.ini
        """
}

process search_database_Comet {
    container params.docker_image_openms
    publishDir "${params.results_root_dir}/${sample}/OpenMS-${params.openms_version}/output/per_fraction/Comet", mode: 'copy', pattern: '*.idXML'
    input:
        tuple val(sample), path(mzml)
        path db
        path ini
        path default_params
    output:
        tuple val(sample), path(output_idxml)
    script:
        output_idxml = "${mzml.baseName}_Comet.idXML"
        def defaults = default_params.name == 'NO_FILE' ? '' : "-default_params_file ${default_params}"
        """
        set -euo pipefail
        CometAdapter -in ${mzml} -out ${output_idxml} -threads ${task.cpus} \\
          -database ${db} -ini ${ini} ${defaults}
        """
}

workflow workflow_search_database_Comet {
    take:
        mzml_file
    main:
        create_json_Comet()
        create_ini_Comet(create_json_Comet.out)
        search_database_Comet(mzml_file, file(params.decoy_database), create_ini_Comet.out, file(params.comet_default_params))
        merge_idxml(search_database_Comet.out.groupTuple(), 'Comet')
        if (params.export_mzTab) export_mzTab(merge_idxml.out)
}

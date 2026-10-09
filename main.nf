/**
 * Database search of tandem mass spectra from one sample or isobaric plex.
 */
nextflow.enable.dsl = 2

include { print_prelogue; read_input_mzml } from "${projectDir}/modules/common"
include { reindex_mzml } from "${projectDir}/modules/reindex_mzml"
include { workflow_search_database_Comet as workflow_Comet } from "${projectDir}/modules/search_database_Comet"
include { workflow_search_database_Sage as workflow_Sage } from "${projectDir}/modules/search_database_Sage"
include { workflow_search_database_MSFragger as workflow_MSFragger } from "${projectDir}/modules/search_database_MSFragger"

print_prelogue()

workflow {
    mzml_file = read_input_mzml(params.input_csv)

    if (params.reindex_mzml) {
        reindex_mzml(mzml_file.collect(), file("${projectDir}/src/ReindexMzML.py"))
        individual_mzML = reindex_mzml.out[0].flatten()
    } else {
        individual_mzML = mzml_file
    }

    if ('Comet' in params.search_engines) {
        workflow_Comet(individual_mzML)
    }
    if ('Sage' in params.search_engines) {
        workflow_Sage(individual_mzML)
    }
    if ('MSFragger' in params.search_engines) {
        workflow_MSFragger(individual_mzML)
    }
}

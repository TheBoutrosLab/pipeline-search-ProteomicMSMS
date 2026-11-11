/**
 * Database search of tandem mass spectra from one or more samples or plexes.
 */
nextflow.enable.dsl = 2

include { print_prelogue; read_input_mzml } from "${projectDir}/modules/common"
include { reindex_mzml } from "${projectDir}/modules/reindex_mzml"
include { workflow_search_database_Comet as workflow_Comet } from "${projectDir}/modules/search_database_Comet"
include { workflow_search_database_Sage as workflow_Sage } from "${projectDir}/modules/search_database_Sage"
include { workflow_search_database_MSFragger as workflow_MSFragger } from "${projectDir}/modules/search_database_MSFragger"

print_prelogue()

workflow {
    sample_mzml = read_input_mzml(params.input_csv)

    if (params.reindex_mzml) {
        reindex_mzml(sample_mzml.groupTuple())
        individual_mzML = reindex_mzml.out.flatMap { sample, files ->
            (files instanceof List ? files : [files]).collect { mzml -> tuple(sample, mzml) }
        }
    } else {
        individual_mzML = sample_mzml
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

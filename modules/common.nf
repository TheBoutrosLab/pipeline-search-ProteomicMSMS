
def print_prelogue() {
    def option_msg = ''
    exclude_args = [
        'input_csv', 'decoy_database', 'output_dir', 'openms_version', 'docker_image_openms',
        'max_cpus', 'max_memory'
    ]
    params.each { key, val ->
        if (!(key in exclude_args)) {
            val = val as String
            option_msg += "\n" + ' ' * 12 + "${key}: ${val}"
        }
    }
    log.info """\
        ===========================================================
        P I P E L I N E   S E A R C H   P R O T E O M I C   M S M S
        ===========================================================
        Boutros Lab

        Current Configuration:
        - pipeline:
            name   : ${workflow.manifest.name}
            version: ${workflow.manifest.version}

        - input:
            input_csv      : ${params.input_csv}
            decoy_database : ${params.decoy_database}

        - output:
            output_dir: ${params.output_dir}

        - options: ${option_msg}

        Tools Used:
            OpenMS: ${params.docker_image_openms}

        ------------------------------------
        Starting workflow...
        ------------------------------------
        """
        .stripIndent()
}

def addArg(args, key, val){
    if (val in Map) {
        if (!args.containsKey(key)) {
            args[key] = [:]
        }
        for (k in val.keySet()) {
            addArg(args[key], k, val[k])
        }
    } else {
        args[key] = val
    }
}

def generateAdapterConfig(String adapter) {
    def Map args = [:]
    def adapter_params = params.containsKey(adapter) ? params[adapter] : [:]
    for (param in adapter_params.keySet()) {
        value = adapter_params[param]
        addArg(args, param, value)
    }
    def Map final_args = [:]
    final_args[adapter] = ['1': args]
    return final_args
}

/** Read fraction mzML paths in CSV order. One launch is one sample or plex. */
def read_input_mzml(String csv_path) {
    def csv = file(csv_path)
    return Channel.fromPath(csv).splitCsv(header: true)
        .map { row ->
            if (row.size() != 1 || !row.path?.trim()) {
                throw new IllegalArgumentException('Input CSV must contain exactly one nonempty path column')
            }
            def mzml = file(row.path.trim().startsWith('/') ? row.path.trim() : "${csv.parent}/${row.path.trim()}")
            if (!mzml.exists() || !mzml.name.toLowerCase().endsWith('.mzml')) {
                throw new IllegalArgumentException("Missing mzML input: ${mzml}")
            }
            return mzml
        }
        .ifEmpty { throw new IllegalArgumentException('Input CSV contains no mzML files') }
}

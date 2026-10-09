# Modifications

## General

For Comet and Sage, amino acid residue modifications can be specified using `variable_modifications` and `fixed_modifications`. Both accept a list of [unimod](http://www.unimod.org) terms. See [here](https://abibuilder.informatik.uni-tuebingen.de/archive/openms/Documentation/nightly/html/TOPP_CometAdapter.html) under `variable_modifications` to see a complete list of supported modification terms.

Example:

```groovy
variable_modifications = [
	'Oxidation (M)'
]
fixed_modifications = [
	'Carbamidomethyl (C)'
]
```

MSFragger, however, uses its own syntax to specify residue modifications. For variable modifications, the syntax is `<mass> <position>`. See [here](https://github.com/Nesvilab/MSFragger/wiki/Setting-the-Parameters#variable_mod_01--16). The syntax for position is explained below.

```
* is used to represent any amino acid
^ is used to represent a terminus
[ is a modifier for protein N-terminal
] is a modifier for protein C-terminal
n is a modifier for peptide N-terminal
c is a modifier for peptide C-terminal
```

In the config file of this pipeline, we specify masses and positions separately as what is used by MSFraggerAdapper from OpenMS. The example below is equivalent of '15.99491 M 3' (oxidation (M))

```groovy
masses = [
	15.99491
]
syntaxes = [
	'M 3'
]
```

The 'position' part can also take an integer to specify the max occurrence per peptide. For example, the example above means there can be up to 3 oxiation on methinione per peptide.

Fixed modifications are specified in MSFragger as the exact mass being added to the particular amino acid residue. The example below adds the TMT6/TMT10/TMT11 tag to all lysine residue. For TMT16/18, use 'add_k_lysine = 304.207146'.

```groovy
add_K_lysine = 229.162932
```

The mass of the modification can be found from [unimode](http://www.unimod.org).

> :warning: Make sure to use the Monoisotopic mass!

## Modification for isobaric labels

For isobaric labelled experiments, the corresponding modification **MUST** be specified. The unimod term and monoisotopic mass can be found from [unimode](http://www.unimod.org). Some types of TMT/iTRAQ plex don't have a corresponding unimod term because they share the same molecule structure and mass with others. For example, The molecular tag of TMT10 and TMT11 is the same as TMT6, thus the term `TMT6plex` can be used for them.

Isobaric labels are usually added to the peptide N-terminus, lysine, and serine residues. We recommand to set fixed modification for N-terminal and lysine and variable modification on serine. If you would like to access the label efficiency, the N-terminal modification can be set to variable.

## Recommended Modifications

We recommend to include methionine oxidation, peptide N-terminal glutamine deamidation as variable modification and cysteine carbamidomethylation (product of disulfide bond cleavage) in every search.

```groovy
variable_modifications = [
	'Oxidation (M)',
	'Gln->pyro-Glu (N-term Q)'
]
fixed_modifications = [
	'Carbamidomethyl (C)'
]

masses = [
	15.99491,         // Oxidation (M)
	-17.026549        // Gln->pyro-Glu (N-term Q)
]
syntaxes = [
	'M 3',            // Oxidation (M)
	'nQ 1'            // Gln->pyro-Glu (N-term Q)
]
add_C_cysteine = 57.021464
```

Protein N-terminal acetylation is also often used as a variable modification.

```groovy
variable_modifications = [
	'Acetyl (Protein N-term)'
]
messes = [
	42.010565
]
syntaxes = [
	'[^ 1'
]
```

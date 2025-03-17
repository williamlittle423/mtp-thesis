import numpy as np
from ase import Atoms
from ase.io.lammpsdata import write_lammps_data  # Import LAMMPS writer from ASE

# Initial lattice parameter for BCC Lithium
lattice_constant = 3.51
primitive_cell = Atoms(
    symbols="Li2",
    positions=[[0, 0, 0], [0.5 * lattice_constant, 0.5 * lattice_constant, 0.5 * lattice_constant]],
    cell=[[lattice_constant, 0, 0], [0, lattice_constant, 0], [0, 0, lattice_constant]],
    pbc=True,
)

# Hydrostatic strains
hydrostatic_strains = [-0.02, -0.01, 0.00, 0.01, 0.02]

# Shear strains (random)
shear_strains = [
    [[1, s12, s13], [s12, 1, s23], [s13, s23, 1]]
    for s12, s13, s23 in np.random.uniform(-0.02, 0.02, size=(4, 3))
]

# Generate configurations
configurations = []

# Apply hydrostatic strains
for strain in hydrostatic_strains:
    scaled_cell = primitive_cell.cell * (1 + strain)
    strained_structure = primitive_cell.copy()
    strained_structure.set_cell(scaled_cell)
    configurations.append(strained_structure)

# Apply shear strains
for shear in shear_strains:
    strained_structure = primitive_cell.copy()
    strained_structure.set_cell(np.dot(primitive_cell.cell, shear))
    configurations.append(strained_structure)

# Save configurations
for i, config in enumerate(configurations):
    write_lammps_data(f"Li_config_{i+1}.data", config)  # Use write_lammps_data to save in LAMMPS format

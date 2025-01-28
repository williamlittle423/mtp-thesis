import os
import subprocess
import re
import numpy as np
import matplotlib.pyplot as plt

# Path to the Quantum ESPRESSO executable
qe_executable = "/Users/williamlittle/software/qe/q-e-qe-7.0/build/bin/pw.x"

# Define a range of initial lattice parameters for relaxation
initial_lattice_parameters = [2.0 + 0.15 * i for i in range(10)]

# List to store the final energies from each relaxation
energies = []

for lat in initial_lattice_parameters:
    # Prepare the input file content for vc-relax
    input_content = f"""
&CONTROL
    calculation = 'vc-relax'
    prefix = 'Li'
    outdir = './tmp/'
    pseudo_dir = '../../pseudopotentials/'
/
&SYSTEM
    ibrav = 3,
    celldm(1) = {lat},  ! Initial lattice parameter
    nat = 2,
    ntyp = 1,
    ecutwfc = 65,
    ecutrho = 260,
/
&ELECTRONS
    conv_thr = 1.0d-8
    mixing_beta = 0.7
/
&IONS
    ion_dynamics = 'bfgs'  ! Ionic relaxation algorithm
/
&CELL
    cell_dynamics = 'bfgs'  ! Cell relaxation algorithm
    cell_dofree = 'all'     ! Allow all cell parameters to relax
/
ATOMIC_SPECIES
 Li  6.94  Li.pbe-s-kjpaw_psl.1.0.0.UPF

ATOMIC_POSITIONS (crystal)
 Li 0.0  0.0  0.0
 Li 0.5  0.5  0.5

K_POINTS automatic
 8  8  8 0 0 0
"""

    # Write the input content to a temporary input file
    input_filename = "temp_vcrelax.in"
    with open(input_filename, "w") as f:
        f.write(input_content)

    # Run the Quantum ESPRESSO calculation using MPI
    output_filename = "temp_vcrelax.out"
    command = f"mpirun -np 4 {qe_executable} -in {input_filename} > {output_filename}"
    subprocess.run(command, shell=True, check=True)

    # Parse the output file to extract the final energy
    with open(output_filename, "r") as out:
        energy = None
        for line in out:
            if "!" in line:
                # Extract the energy value using regular expressions
                match = re.search(r"[-+]?\d*\.\d+|\d+", line.split('=')[-1])
                if match:
                    energy = float(match.group(0))
                    energies.append(energy)
                break

    print(f"Lattice parameter: {lat}, Energy: {energy} Ry")

# Optionally, plot the energies versus initial lattice parameters
plt.figure(figsize=(8, 6))
plt.plot(initial_lattice_parameters, energies, marker='o')
plt.title('Energy vs. Initial Lattice Parameter for vc-relax')
plt.xlabel('Initial Lattice Parameter (celldm(1))')
plt.ylabel('Total Energy (Ry)')
plt.grid(True)
plt.show()




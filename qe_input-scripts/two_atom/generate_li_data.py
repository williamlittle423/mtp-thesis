import os
import subprocess
import re
import numpy as np

qe_executable = "/Users/williamlittle/software/qe/q-e-qe-7.0/build/bin/pw.x"  # Replace with the actual path to pw.x


energies = []

for ecut in ecutwfc_values:
    # Prepare input file
    input_content = f"""
&CONTROL
    calculation = 'scf'
    prefix = 'Li'
    outdir = './tmp/'
    pseudo_dir = '../../pseudopotentials/'
/
&SYSTEM
    ibrav = 3,
    celldm(1) = 6.40,
    nat = 2,
    ntyp = 1,
    ecutwfc = {ecut},
    ecutrho = {ecut * 4},
/
&ELECTRONS
    conv_thr    = 1.0d-8
    mixing_beta = 0.7
/
ATOMIC_SPECIES
 Li  6.94  Li.pbe-s-kjpaw_psl.1.0.0.UPF

ATOMIC_POSITIONS (crystal)
 Li 0.0  0.0  0.0
 Li 0.5  0.5  0.5

K_POINTS automatic
 8  8  8  0  0  0
"""

    with open("temp_scf.in", "w") as f:
        f.write(input_content)

    # Run QE
    subprocess.run(f"mpirun -np 4 {qe_executable} -in temp_scf.in > temp_scf.out", shell=True)

    # Parse energy
    with open("temp_scf.out", "r") as out:
        energy = None
        for line in out:
            if "!" in line:
                match = re.search(r"[-+]?\d*\.\d+|\d+", line.split('=')[-1])
                if match:
                    energy = float(match.group(0))
                    energies.append(energy)
                break

    print(f"ecutwfc = {ecut} Ry -> Total energy = {energy} Ry")

# Analyze energies vs ecutwfc ...


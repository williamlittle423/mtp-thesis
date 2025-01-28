import os
import numpy as np
import subprocess

# Parameters for equilibrium configuration
equilibrium_celldm = 10.487  # in Bohr
perturbation_scale = 0.10  # Maximum relative perturbation
num_configurations = 10

# Base atomic positions
base_positions = np.array([
    [0.0, 0.0, 0.0],
    [0.5, 0.5, 0.5]
])

# Output directories
qe_outputs_dir = "qe_outputs"
os.makedirs(qe_outputs_dir, exist_ok=True)

perturbation = np.arange(-perturbation_scale, perturbation_scale, 0.025)

print('Perturbation range: ', perturbation)

qe_binary = "pw.x"

# Generate perturbed configurations and run simulations
for i, p in enumerate(perturbation):
    # Apply random perturbation to celldm
    perturbed_celldm = equilibrium_celldm*(1 + p)
    print(f"Perturbed celldm: {perturbed_celldm}")

    # Apply fixed perturbation to atomic positions
    perturbed_positions = base_positions * (1 + p)
    print(f"Perturbed positions: {perturbed_positions}")

    # Ensure positions remain within bounds [0, 1] (crystal coordinates)
    perturbed_positions = perturbed_positions % 1.0

    # Generate QE input file
    input_filename = f"Li_config_{i + 1}.in"


    with open(input_filename, "w") as f:
        f.write(f"""
&CONTROL
    calculation = 'scf',
    prefix = 'Li_config_{i + 1}',
    outdir = './tmp/',
    pseudo_dir = '../../pseudopotentials/',
    tprnfor = .true.,
    tstress = .true.,
/
&SYSTEM
    ibrav = 1,
    celldm(1) = {perturbed_celldm:.6f},  ! Perturbed lattice parameter
    nat = 2,
    ntyp = 1,
    ecutwfc = 65.0,
    ecutrho = 300.0,
    occupations = 'smearing',
    smearing = 'gaussian',
    degauss = 0.01,
/
&ELECTRONS
    conv_thr = 1.0d-8,
    mixing_beta = 0.7,
/
ATOMIC_SPECIES
 Li  6.94  Li.pbe-s-kjpaw_psl.1.0.0.UPF
ATOMIC_POSITIONS (crystal)
""")
        for pos in perturbed_positions:
            f.write(f" Li  {pos[0]:.6f}  {pos[1]:.6f}  {pos[2]:.6f}\n")

        f.write("""
K_POINTS automatic
 4 4 4 0 0 0
""")

    # Run QE simulation
    output_filename = os.path.join(qe_outputs_dir, f"Li_config_{i + 1}.out")
    with open(output_filename, "w") as output_file:
        try:
            print(f"Running QE for configuration {i + 1}...")
            subprocess.run([qe_binary, "-in", input_filename], stdout=output_file, stderr=subprocess.STDOUT, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running QE for configuration {i + 1}: {e}")
        except FileNotFoundError:
            print("Error: Quantum ESPRESSO binary not found.")
            break
    # make a directory to store the input files
    os.makedirs('qe_inputs', exist_ok=True)
    os.system(f'mv {input_filename} qe_inputs')

print(f"All configurations have been run. Outputs are stored in '{qe_outputs_dir}'.")

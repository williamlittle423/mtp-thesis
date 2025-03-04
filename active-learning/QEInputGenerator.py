

""
import os
import numpy as np
import subprocess

class QEInputGenerator:
    def __init__(self, equilibrium_celldm, perturbation_scale, qe_binary, base_positions, qe_outputs_dir="qe_outputs"):
        """
        Initialize the QEInputGenerator class with parameters for generating perturbed configurations.
        """
        self.equilibrium_celldm = equilibrium_celldm  # Lattice parameter in Bohr
        self.perturbation_scale = perturbation_scale  # Maximum relative perturbation
        self.qe_binary = qe_binary  # Path to Quantum ESPRESSO binary (pw.x)
        self.base_positions = base_positions  # Base atomic positions (fractional coordinates)
        self.qe_outputs_dir = qe_outputs_dir  # Directory to store QE output files
        os.makedirs(self.qe_outputs_dir, exist_ok=True)  # Create output directory if it doesn't exist

    def generate_and_run_configurations(self, num_configurations=10):
        """
        Generate perturbed configurations and run Quantum ESPRESSO simulations.
        """
        for i in range(1, num_configurations + 1):
            # Apply random perturbation to celldm
            perturbed_celldm = self.equilibrium_celldm * (
                1 + np.random.uniform(-self.perturbation_scale, self.perturbation_scale)
            )

            # Apply random perturbation to atomic positions
            perturbed_positions = self.base_positions + np.random.uniform(
                -self.perturbation_scale, self.perturbation_scale, self.base_positions.shape
            )

            # Ensure positions remain within bounds [0, 1] (crystal coordinates)
            perturbed_positions = perturbed_positions % 1.0

            # Generate QE input file
            input_filename = f"Li_config_{i}.in"
            with open(input_filename, "w") as f:
                f.write(f"""
&CONTROL
    calculation = 'scf',
    prefix = 'Li_config_{i}',
    outdir = './tmp/',
    pseudo_dir = '../pseudopotentials/',
    tprnfor = .true.,
    tstress = .true.,
/
&SYSTEM
    ibrav = 1,
    celldm(1) = {perturbed_celldm:.6f},  ! Perturbed lattice parameter
    nat = {len(perturbed_positions)},
    ntyp = 1,
    ecutwfc = 30.0,
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
            output_filename = os.path.join(self.qe_outputs_dir, f"Li_config_{i}.out")
            with open(output_filename, "w") as output_file:
                try:
                    print(f"Running QE for configuration {i}...")
                    subprocess.run(
                        [self.qe_binary, "-in", input_filename],
                        stdout=output_file,
                        stderr=subprocess.STDOUT,
                        check=True,
                    )
                except subprocess.CalledProcessError as e:
                    print(f"Error running QE for configuration {i}: {e}")
                except FileNotFoundError:
                    print("Error: Quantum ESPRESSO binary not found.")
                    break

        print(f"All configurations have been run. Outputs are stored in '{self.qe_outputs_dir}'.")


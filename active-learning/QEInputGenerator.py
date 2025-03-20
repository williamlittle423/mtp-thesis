import os
import numpy as np
import subprocess
import math

import os
import numpy as np
import subprocess
import math

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
            # Apply random perturbation to celldm (stays within ~2% of equilibrium)
            perturbed_celldm = self.equilibrium_celldm * (
                1 + np.random.uniform(-self.perturbation_scale, self.perturbation_scale)
            )

            # Convert base positions to Cartesian
            cartesian_positions = self.base_positions * perturbed_celldm

            # Apply random perturbation in Cartesian coordinates
            cartesian_positions += np.random.uniform(
                -self.perturbation_scale, self.perturbation_scale, cartesian_positions.shape
            )

            # Convert back to fractional coordinates (ensures atoms stay within unit cell)
            perturbed_positions = cartesian_positions / perturbed_celldm

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
    ibrav = 3,
    celldm(1) = {perturbed_celldm:.6f}, 
    nat = {len(perturbed_positions)},
    ntyp = 1,
    ecutwfc = 60.0,
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
8 8 8 0 0 0 
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

    def convert_preselected(self):
        """
        Reads multiple preselected configuration files and generates QE input files with unique indices.
        """
        input_files = []
        file_counter = 1  # Start from 1 and ensure unique indices for each input file
        
        preselected_files = [f"out/preselected.cfg.{x}" for x in range(1, 10) if os.path.exists(f"out/preselected.cfg.{x}")]
        
        print(f"Found {len(preselected_files)} preselected configuration files.")

        for cfg_filename in preselected_files:
            print(f"Processing {cfg_filename}...")

            configurations = QEInputGenerator.parse_preselected_cfg(cfg_filename)
            
            for supercell, atoms in configurations:
                lattice_const = QEInputGenerator._vector_length(supercell[0])
                frac_positions = QEInputGenerator._cartesian_to_fractional(atoms, lattice_const)
                
                qe_input_str = QEInputGenerator.generate_qe_input(lattice_const, frac_positions, config_index=file_counter)
                output_filename = f"qe_outputs_train_set/Li_preselected_{file_counter}.in"
                
                with open(output_filename, "w") as f:
                    f.write(qe_input_str)

                print(f"Generated QE input: {output_filename}")
                input_files.append(output_filename)
                file_counter += 1  # Ensure unique numbering across all files

        return input_files


    def run_preselected(self, input_files):
        """
        Runs the Quantum Espresso simulations only once per unique input file.
        """
        output_files = []
        
        # Ensure each file is executed only once
        unique_input_files = list(set(input_files))  # Convert to set to remove duplicates

        for input_file in unique_input_files:
            output_file = input_file.replace(".in", ".out")
            output_files.append(output_file)

            with open(output_file, "w") as output:
                try:
                    print(f"Running QE for {input_file}...")
                    subprocess.run(
                        [self.qe_binary, "-in", input_file],
                        stdout=output,
                        stderr=subprocess.STDOUT,
                        check=True,
                    )
                    print(f"QE output saved: {output_file}")
                except subprocess.CalledProcessError as e:
                    print(f"Error running QE for {input_file}: {e}")
                except FileNotFoundError:
                    print("Error: Quantum ESPRESSO binary not found.")
                    break

        return output_files


        return output_files

    @staticmethod
    def parse_preselected_cfg(filename):
        """
        Parse MLIP preselected configurations from a CFG file.
        """
        configurations = []
        current_supercell = []
        current_atoms = []
        reading_supercell = False
        reading_atomdata = False

        with open(filename, 'r') as file:
            for line in file:
                tokens = line.split()
                if not tokens:
                    continue

                if tokens[0] == "BEGIN_CFG":
                    current_supercell = []
                    current_atoms = []
                    reading_supercell = False
                    reading_atomdata = False
                    continue
                elif tokens[0] == "Supercell":
                    reading_supercell = True
                    reading_atomdata = False
                    continue
                elif tokens[0] == "AtomData:":
                    reading_supercell = False
                    reading_atomdata = True
                    continue
                elif tokens[0] == "END_CFG":
                    if current_supercell and current_atoms:
                        configurations.append((current_supercell, current_atoms))
                    continue

                if reading_supercell and len(tokens) == 3:
                    current_supercell.append([float(t) for t in tokens])
                elif reading_atomdata and len(tokens) >= 5:
                    try:
                        current_atoms.append({
                            'id': int(tokens[0]),
                            'type': int(tokens[1]),
                            'x': float(tokens[2]),
                            'y': float(tokens[3]),
                            'z': float(tokens[4])
                        })
                    except ValueError:
                        continue

        return configurations

    @staticmethod
    def _vector_length(vec):
        """Computes the Euclidean norm of a 3D vector."""
        return math.sqrt(vec[0]**2 + vec[1]**2 + vec[2]**2)

    @staticmethod
    def _cartesian_to_fractional(atoms, lattice_const):
        """
        Converts Cartesian positions to fractional (crystal) coordinates.
        """
        return [[atom['x'] / lattice_const, atom['y'] / lattice_const, atom['z'] / lattice_const] for atom in atoms]

    @staticmethod
    def generate_qe_input(lattice_const, frac_positions, config_index=1):
        """
        Generate Quantum ESPRESSO input file content.
        """
        qe_input = f"""&CONTROL
    calculation = 'scf',
    prefix = 'Li_preselected_{config_index}',
    outdir = './tmp/',
    pseudo_dir = '../pseudopotentials/',
    tprnfor = .true.,
    tstress = .true.,
/
&SYSTEM
    ibrav = 1,
    celldm(1) = {lattice_const:.6f},
    nat = {len(frac_positions)},
    ntyp = 1,
    ecutwfc = 60.0,
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
"""
        for pos in frac_positions:
            qe_input += f" Li  {pos[0]:.6f}  {pos[1]:.6f}  {pos[2]:.6f}\n"

        qe_input += "\nK_POINTS automatic\n8 8 8 0 0 0\n"
        return qe_input


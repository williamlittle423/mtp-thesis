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

    @staticmethod
    def parse_preselected_cfg(filename):
        """
        Parses the input CFG file to extract the supercell lattice vectors and atomic positions
        for one or more configurations. Each configuration is delimited by BEGIN_CFG and END_CFG.
        
        Returns:
            A list of tuples: [(supercell1, atoms1), (supercell2, atoms2), ...]
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
                    # Start a new configuration
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
                    # End current configuration; store if any data was collected.
                    if current_supercell and current_atoms:
                        configurations.append((current_supercell, current_atoms))
                    current_supercell = []
                    current_atoms = []
                    reading_supercell = False
                    reading_atomdata = False
                    continue
                elif tokens[0] == "Feature":
                    continue

                # Parse supercell vectors (three numbers per line)
                if reading_supercell:
                    if len(tokens) >= 3:
                        try:
                            vec = [float(tokens[0]), float(tokens[1]), float(tokens[2])]
                            current_supercell.append(vec)
                        except ValueError:
                            continue
                # Parse atomic positions
                elif reading_atomdata:
                    if tokens[0].isdigit() and len(tokens) >= 5:
                        try:
                            atom = {
                                'id': int(tokens[0]),
                                'type': int(tokens[1]),
                                'x': float(tokens[2]),
                                'y': float(tokens[3]),
                                'z': float(tokens[4])
                            }
                            current_atoms.append(atom)
                        except (ValueError, IndexError):
                            continue

        return configurations

    @staticmethod
    def _vector_length(vec):
        """Computes the Euclidean norm of a 3D vector."""
        return math.sqrt(vec[0]**2 + vec[1]**2 + vec[2]**2)

    @staticmethod
    def _cartesian_to_fractional(atoms, lattice_const):
        """
        For a cubic cell with lattice parameter lattice_const, converts Cartesian positions (in Angstrom)
        to fractional coordinates.
        """
        frac_positions = []
        for atom in atoms:
            frac = [atom['x']/lattice_const,
                    atom['y']/lattice_const,
                    atom['z']/lattice_const]
            frac_positions.append(frac)
        return frac_positions

    @staticmethod
    def generate_qe_input(lattice_const, frac_positions, config_index=1):
        """
        Generates a Quantum Espresso input string in the desired format.
        Uses ibrav=1 (cubic) and writes the atomic positions in crystal (fractional) coordinates.
        """
        qe_input = f"""&CONTROL
        calculation = 'scf',
        prefix = 'Li_config_{config_index}',
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
    """
        for pos in frac_positions:
            qe_input += f" Li  {pos[0]:.6f}  {pos[1]:.6f}  {pos[2]:.6f}\n"

        qe_input += """
    K_POINTS automatic
    4 4 4 0 0 0
    """
        return qe_input

    def convert_preselected(self):
        """
        Reads the preselected configuration from 'out/preselected.cfg.0' and converts each configuration to
        a separate Quantum Espresso input file. Each is saved as 'Li_preselected_{i}.in'.
        """
        
        cfg_filename = "out/preselected.cfg.0"
        configurations = QEInputGenerator.parse_preselected_cfg(cfg_filename)
        if not configurations:
            print("Error: No valid configuration found in the preselected file.")
            return
        
        input_files = []

        for i, (supercell, atoms) in enumerate(configurations, start=1):
            # Compute the lattice parameter as the norm of the first supercell vector (assumed cubic)
            lattice_const = QEInputGenerator._vector_length(supercell[0])
            # Convert atomic positions (in Angstrom) to fractional (crystal) coordinates
            frac_positions = QEInputGenerator._cartesian_to_fractional(atoms, lattice_const)
            # Generate the QE input string for this configuration
            qe_input_str = QEInputGenerator.generate_qe_input(lattice_const, frac_positions, config_index=i)
            output_filename = f"Li_preselected_{i}.in"
            input_files.append(output_filename)
            with open(output_filename, "w") as f:
                f.write(qe_input_str)
            print(f"Quantum Espresso input file has been generated: {output_filename}")

        return input_files


    def run_preselected(self, input_files):
        """
        Runs the preselected configurations using Quantum Espresso.
        """
        output_files = []
        
        for input_file in input_files:
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
                except subprocess.CalledProcessError as e:
                    print(f"Error running QE for {input_file}: {e}")
                except FileNotFoundError:
                    print("Error: Quantum ESPRESSO binary not found.")
                    break

        print(f"All preselected configurations have been run. Outputs are stored in '{self.qe_outputs_dir}'.")
        return output_files



from QEInputGenerator import QEInputGenerator
from QEOutputParser import QEOutputParser
import numpy as np

if __name__ == "__main__":
    # Step 1: Define parameters for the 1-atom BCC primitive cell
    EQUILIBRIUM_CELLDM = 6.63  # BCC lattice parameter in Bohr
    NUM_CONFIGURATIONS = 20    # Number of configurations to generate

    # Define perturbation range: from -12.5% to +12.5%
    MIN_PERTURBATION = -0.125
    MAX_PERTURBATION = 0.125

    # Base atomic positions for a BCC cell (fractional coordinates):
    BASE_POSITIONS_UNIT_CELL = np.array([
        [0.0, 0.0, 0.0],
        [0.5, 0.5, 0.5]
    ])

    print(f"Generated a primitive BCC unit cell with {len(BASE_POSITIONS_UNIT_CELL)} atom(s).")

    # Initialize the QEInputGenerator (it uses the base positions; perturbation scale is not used in a random sense here)
    generator = QEInputGenerator(
        equilibrium_celldm=EQUILIBRIUM_CELLDM,
        perturbation_scale=MAX_PERTURBATION,  # Not directly used now
        qe_binary="pw.x",
        base_positions=BASE_POSITIONS_UNIT_CELL,
        qe_outputs_dir="qe_outputs_train_set"
    )
    
    print("Generating evenly spaced perturbed configurations and running QE...")

    for i in range(1, NUM_CONFIGURATIONS + 1):
        # Calculate a deterministic perturbation factor that ranges from MIN_PERTURBATION to MAX_PERTURBATION
        perturbation_factor = MIN_PERTURBATION + (i - 1) / (NUM_CONFIGURATIONS - 1) * (MAX_PERTURBATION - MIN_PERTURBATION)
        perturbed_celldm = EQUILIBRIUM_CELLDM * (1 + perturbation_factor)
        
        # For a uniform expansion/compression, the fractional atomic positions remain the same.
        perturbed_positions = BASE_POSITIONS_UNIT_CELL
        
        # Generate QE input file with the updated lattice parameter
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
        
        # Run QE simulation for this input
        output_filename = f"qe_outputs_train_set/Li_config_{i}.out"
        try:
            print(f"Running QE for configuration {i} with celldm = {perturbed_celldm:.6f}...")
            import subprocess
            with open(output_filename, "w") as output_file:
                subprocess.run(
                    [generator.qe_binary, "-in", input_filename],
                    stdout=output_file,
                    stderr=subprocess.STDOUT,
                    check=True,
                )
        except subprocess.CalledProcessError as e:
            print(f"Error running QE for configuration {i}: {e}")
        except FileNotFoundError:
            print("Error: Quantum ESPRESSO binary not found.")
            break

    print(f"All {NUM_CONFIGURATIONS} configurations have been run. Outputs are stored in 'qe_outputs_train_set'.")

    # Step 3: Parse QE outputs and create initial training set
    parser = QEOutputParser()
    qe_output_files = [f"qe_outputs_train_set/Li_config_{i}.out" for i in range(1, NUM_CONFIGURATIONS + 1)]
    
    print("Parsing QE outputs and writing train.cfg...")
    parser.write_mtp_configurations(qe_output_files, mtp_config_file="train.cfg")

    print("Initial training set written to train.cfg.")

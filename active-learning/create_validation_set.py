from QEInputGenerator import QEInputGenerator
from QEOutputParser import QEOutputParser
import numpy as np

if __name__ == "__main__":
    # Step 1: Define parameters for the 1-atom BCC primitive cell
    EQUILIBRIUM_CELLDM = 6.63  # BCC lattice parameter in Bohr
    PERTURBATION_SCALE = 0.05   # Maximum relative perturbation (±5%)
    NUM_CONFIGURATIONS = 5     # Number of configurations to generate

    # Base atomic position for a single BCC unit cell (1 atom at the corner)
    BASE_POSITIONS_UNIT_CELL = np.array([
        [0.0, 0.0, 0.0]  # Atom at the origin (primitive cell)
    ])

    print(f"Generated a primitive BCC unit cell with {len(BASE_POSITIONS_UNIT_CELL)} atom(s).")

    # Step 2: Generate perturbed configurations and run QE simulations
    generator = QEInputGenerator(
        equilibrium_celldm=EQUILIBRIUM_CELLDM,
        perturbation_scale=PERTURBATION_SCALE,
        qe_binary="pw.x",
        base_positions=BASE_POSITIONS_UNIT_CELL,
        qe_outputs_dir="qe_outputs_validation_set"
    )
    
    print("Generating perturbed configurations and running QE...")
    generator.generate_and_run_configurations(num_configurations=NUM_CONFIGURATIONS)

    # Step 3: Parse QE outputs and create initial validation set
    parser = QEOutputParser()
    qe_output_files = [
        f"qe_outputs_validation_set/Li_config_{i + 1}.out" for i in range(NUM_CONFIGURATIONS)
    ]
    
    print("Parsing QE outputs and writing validation.cfg...")
    parser.write_mtp_configurations(qe_output_files, mtp_config_file="validation.cfg")

    print("Initial validation set written to validation.cfg.")

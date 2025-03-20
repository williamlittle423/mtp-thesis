from QEInputGenerator import QEInputGenerator
from QEOutputParser import QEOutputParser
import numpy as np
import glob
import os

if __name__ == "__main__":
    # Path to preselected configurations
    preselected_pattern = "out/preselected.cfg.[1-9]"  # Matches preselected.cfg.1 to preselected.cfg.9
    preselected_files = sorted(glob.glob(preselected_pattern))

    if not preselected_files:
        print("No new preselected configurations found. Exiting.")
        exit(1)

    print(f"Found {len(preselected_files)} preselected configuration files.")

    # Define QE parameters (although these are not directly used in preselected processing)
    EQUILIBRIUM_CELLDM = 6.63  # Lattice parameter in Bohr
    PERTURBATION_SCALE = 0.10  # Not used, but kept for consistency
    BASE_POSITIONS_UNIT_CELL = np.array([[0.0, 0.0, 0.0]])  # Base atomic position

    # Initialize QEInputGenerator
    generator = QEInputGenerator(
        equilibrium_celldm=EQUILIBRIUM_CELLDM,
        perturbation_scale=PERTURBATION_SCALE,
        qe_binary="pw.x",
        base_positions=BASE_POSITIONS_UNIT_CELL,
        qe_outputs_dir="qe_outputs_train_set"
    )

    # Convert preselected configurations into QE input files
    print(f"Processing preselected files...")
    input_files = generator.convert_preselected()

    # Run QE simulations
    output_files = generator.run_preselected(input_files)

    # Parse QE outputs and append to MTP training set
    parser = QEOutputParser()
    parser.append_mtp_configurations(output_files, 'train.cfg')

    print("All preselected configurations processed and added to train.cfg.")

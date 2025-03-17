from QEInputGenerator import QEInputGenerator
from QEOutputParser import QEOutputParser
import numpy as np

if __name__ == "__main__":
    # Step 1: Generate a 2x2x2 BCC supercell
    EQUILIBRIUM_CELLDM = 6.63  # BCC lattice parameter in Bohr
    PERTURBATION_SCALE = 0.05   # Maximum relative perturbation
    NUM_CONFIGURATIONS = 10     # Number of configurations to generate

    # Base atomic positions for a single BCC unit cell (2 atoms)
    BASE_POSITIONS_UNIT_CELL = np.array([
        [0.0, 0.0, 0.0],  # Atom at the corner
        [0.5, 0.5, 0.5]   # Atom at the body center
    ])

    # Generate a 2x2x2 supercell (8 unit cells, 16 atoms total)
    BASE_POSITIONS_SUPERCELL = []
    for x in range(2):
        for y in range(2):
            for z in range(2):
                shift = np.array([x / 2.0, y / 2.0, z / 2.0])  # Shift for each unit cell
                BASE_POSITIONS_SUPERCELL.extend(BASE_POSITIONS_UNIT_CELL + shift)
    
    BASE_POSITIONS_SUPERCELL = np.array(BASE_POSITIONS_SUPERCELL) % 1.0  # Ensure positions are within [0,1]

    print(f"Generated a 2x2x2 supercell with {len(BASE_POSITIONS_SUPERCELL)} atoms.")

    # Step 2: Generate perturbed configurations and run QE simulations
    generator = QEInputGenerator(
        equilibrium_celldm=EQUILIBRIUM_CELLDM,
        perturbation_scale=PERTURBATION_SCALE,
        qe_binary="pw.x",
        base_positions=BASE_POSITIONS_SUPERCELL,
        qe_outputs_dir="qe_outputs_train_set"
    )
    
    print("Generating perturbed configurations and running QE...")
    generator.generate_and_run_configurations(num_configurations=NUM_CONFIGURATIONS)

    # Step 3: Parse QE outputs and create initial training set
    parser = QEOutputParser()
    qe_output_files = [
        f"qe_outputs_train_set/Li_config_{i + 1}.out" for i in range(NUM_CONFIGURATIONS)
    ]
    
    print("Parsing QE outputs and writing train.cfg...")
    parser.write_mtp_configurations(qe_output_files, mtp_config_file="train.cfg")

    print("Initial training set written to train.cfg.")

from QEInputGenerator import QEInputGenerator
from QEOutputParser import QEOutputParser
import numpy as np

if __name__ == "__main__":

    # THESE ARE NOT USED
    EQUILIBRIUM_CELLDM = 6.63
    PERTURBATION_SCALE = 0.10
    NUM_CONFIGURATIONS = 10 

    # Base atomic position for a single BCC primitive cell
    BASE_POSITIONS_UNIT_CELL = np.array([
        [0.0, 0.0, 0.0]  # Atom at the origin for primitive cell
    ])

    generator = QEInputGenerator(
        equilibrium_celldm=EQUILIBRIUM_CELLDM,
        perturbation_scale=PERTURBATION_SCALE,
        qe_binary="pw.x",
        base_positions=BASE_POSITIONS_UNIT_CELL,
        qe_outputs_dir="qe_outputs_train_set"
    )

    input_files = generator.convert_preselected()

    output_files = generator.run_preselected(input_files)

    # Step 3: Parse QE outputs and write MTP configurations
    parser = QEOutputParser()

    parser.append_mtp_configurations(output_files, 'train.cfg')
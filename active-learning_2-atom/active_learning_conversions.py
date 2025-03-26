from QEInputGenerator import QEInputGenerator
from QEOutputParser import QEOutputParser
import numpy as np
import os

if __name__ == "__main__":
    # Tuple: (preselected file, number of atoms expected in configuration)
    preselected_files = [
        ('out/preselected_stage1_2atom.cfg.0', 2),
        ('out/preselected_stage2_4atom.cfg.0', 4),
    ]

    for preselected_file, nat in preselected_files:
        if not os.path.isfile(preselected_file):
            print(f"Warning: File {preselected_file} does not exist. Skipping.")
            continue

        print(f"Processing {preselected_file} with {nat} atoms...")

        # Lattice parameter in Bohr (for QE, if using non-ibrav=0, celldm is in Bohr)
        EQUILIBRIUM_CELLDM = 6.63  
        PERTURBATION_SCALE = 0.10

        # Dummy base positions for initialization; they won't be used in convert_preselected_override.
        BASE_POSITIONS_UNIT_CELL = np.array([[0.0, 0.0, 0.0]])

        generator = QEInputGenerator(
            equilibrium_celldm=EQUILIBRIUM_CELLDM,
            perturbation_scale=PERTURBATION_SCALE,
            qe_binary="pw.x",
            base_positions=BASE_POSITIONS_UNIT_CELL,
            qe_outputs_dir="qe_outputs_train_set"
        )

        # Use the override to process the specific preselected file.
        input_files = generator.convert_preselected_override(preselected_file, num_atoms=nat)
        output_files = generator.run_preselected(input_files)

        parser = QEOutputParser()
        parser.append_mtp_configurations(output_files, 'train.cfg')

        print(f"{preselected_file} processed and added to train.cfg.")

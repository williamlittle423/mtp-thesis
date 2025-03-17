import numpy as np

import re

class QEOutputParser:
    def parse_qe_output(self, qe_output):
        """
        Parse Quantum ESPRESSO output file content to extract cell vectors, atomic positions,
        forces, stress tensor, and energy.
        """
        alat = None
        cell_vectors = []
        atom_positions = []
        forces = []
        stress_tensor_raw = []
        energy = None

        lines = qe_output.splitlines()
        for i, line in enumerate(lines):
            # Parse lattice parameter (alat)
            if "lattice parameter (alat)" in line:
                alat = float(line.split("=")[-1].strip().split()[0])

            # Parse cell vectors
            elif "a(1)" in line or "a(2)" in line or "a(3)" in line:
                cell_vectors.append([float(x) for x in line.split("(")[-1].strip(" )").split()])

            # Parse atomic positions
            elif "tau(" in line:
                position_values = line.split("=")[-1].strip(" ()").split()
                atom_positions.append([float(x) for x in position_values])

            # Parse forces
            elif "force =" in line:
                forces.append([float(x) * (13.6057 / 0.529177) for x in line.split("=")[-1].strip().split()])  # Ry/Bohr -> eV/Å

            # Parse stress tensor
            elif "total   stress" in line:
                stress_tensor_raw = [
                    [float(x) * (13.6057 / (0.529177**3)) for x in lines[i + j + 1].split()[:3]]
                    for j in range(3)
                ]

            if "!" in line:
                energy = float(line.split("=")[-1].strip().split()[0]) * 13.6057  # Convert Ry to eV

        # Convert units
        if alat is not None:
            alat *= 0.529177  # Convert alat from Bohr to Å
            cell_vectors = [[v * alat for v in vector] for vector in cell_vectors]  # Convert cell vectors to Å
            atom_positions = [[p * alat for p in pos] for pos in atom_positions]  # Convert positions to Å

        # Reduce the full stress tensor (3x3) to the required six components
        stress_tensor = [
            stress_tensor_raw[0][0],  # xx
            stress_tensor_raw[1][1],  # yy
            stress_tensor_raw[2][2],  # zz
            stress_tensor_raw[1][2],  # yz (or zy)
            stress_tensor_raw[0][2],  # xz (or zx)
            stress_tensor_raw[0][1],  # xy (or yx)
        ]

        return cell_vectors, atom_positions, forces, stress_tensor, energy

    def write_mtp_configurations(self, qe_output_files, mtp_config_file):
        """
        Write parsed Quantum ESPRESSO outputs into an MTP-compatible configuration file.
        """
        with open(mtp_config_file, "w") as cfg_file:
            for qe_output_file in qe_output_files:
                with open(qe_output_file, "r") as file:
                    qe_output = file.read()

                try:
                    cell_vectors, atom_positions, forces, stress_tensor, energy = self.parse_qe_output(qe_output)

                    cfg_file.write("BEGIN_CFG\n")
                    cfg_file.write(f" Size\n    {len(atom_positions)}\n")
                    cfg_file.write(" Supercell\n")
                    for vector in cell_vectors:
                        cfg_file.write(f"   {'      '.join(f'{v:.6f}' for v in vector)}\n")
                    cfg_file.write(" AtomData:  id    type    cartes_x      cartes_y      cartes_z           fx          fy          fz\n")
                    for i, (pos, force) in enumerate(zip(atom_positions, forces), start=1):
                        cfg_file.write(f"            {i}     0       {'      '.join(f'{p:.6f}' for p in pos)}           {'      '.join(f'{f:.6f}' for f in force)}\n")
                    cfg_file.write(" PlusStress: xx          yy          zz          yz          xz          xy\n")
                    cfg_file.write(f"         {'   '.join(f'{s:.6f}' if s < 0 else f' {s:.6f}' for s in stress_tensor)}\n")
                    cfg_file.write(f" Energy\n    {energy:.6f}\n")
                    cfg_file.write("END_CFG\n\n")

                except Exception as e:
                    print(f"Error processing {qe_output_file}: {e}")

    def append_mtp_configurations(self, qe_output_files, mtp_config_file):
        """
        Append parsed Quantum ESPRESSO outputs into an MTP-compatible configuration file.
        """
        # Open the file in append mode ("a")
        with open(mtp_config_file, "a") as cfg_file:
            for qe_output_file in qe_output_files:
                with open(qe_output_file, "r") as file:
                    qe_output = file.read()

                try:
                    cell_vectors, atom_positions, forces, stress_tensor, energy = self.parse_qe_output(qe_output)

                    cfg_file.write("BEGIN_CFG\n")
                    cfg_file.write(f" Size\n    {len(atom_positions)}\n")
                    cfg_file.write(" Supercell\n")
                    for vector in cell_vectors:
                        cfg_file.write(f"   {'      '.join(f'{v:.6f}' for v in vector)}\n")
                    cfg_file.write(" AtomData:  id    type    cartes_x      cartes_y      cartes_z           fx          fy          fz\n")
                    for i, (pos, force) in enumerate(zip(atom_positions, forces), start=1):
                        cfg_file.write(f"            {i}     0       {'      '.join(f'{p:.6f}' for p in pos)}           {'      '.join(f'{f:.6f}' for f in force)}\n")
                    cfg_file.write(" PlusStress: xx          yy          zz          yz          xz          xy\n")
                    cfg_file.write(f"         {'   '.join(f'{s:.6f}' if s < 0 else f' {s:.6f}' for s in stress_tensor)}\n")
                    cfg_file.write(f" Energy\n    {energy:.6f}\n")
                    cfg_file.write("END_CFG\n\n")

                except Exception as e:
                    print(f"Error processing {qe_output_file}: {e}")

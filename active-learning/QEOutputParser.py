import numpy as np
import re

class QEOutputParser:
    def parse_qe_output(self, qe_output):
        """
        Parse Quantum ESPRESSO output file content to extract cell vectors, atomic positions,
        forces, stress tensor, and energy, converting them to MLIP-3 units (eV, eV/Å, eV/Å³).
        """
        E_atom_relaxed = -202.95628621  # Energy of a single atom in the relaxed state
        alat = None
        cell_vectors = []
        atom_positions = []
        forces = []
        stress_tensor_raw = []
        energy = None
        num_atoms = 0  # Track number of atoms

        lines = qe_output.splitlines()  # Split output into lines
        for i, line in enumerate(lines):
            # Parse lattice parameter (alat in Bohr)
            if "lattice parameter (alat)" in line:
                alat = float(line.split("=")[-1].strip().split()[0]) * 0.529177  # Convert Bohr to Å

            # Parse cell vectors
            elif "a(1)" in line or "a(2)" in line or "a(3)" in line:
                cell_vectors.append([float(x) * alat for x in line.split("(")[-1].strip(" )").split()])  # Convert Bohr → Å

            # Parse atomic positions (fractional coordinates)
            elif "tau(" in line:
                position_values = line.split("=")[-1].strip(" ()").split()
                atom_positions.append([float(x) * alat for x in position_values])  # Convert Bohr → Å
                num_atoms += 1  # Count atoms

            # Parse forces (Ry/Bohr → eV/Å)
            elif "force =" in line:
                forces.append([float(x) * 25.711 for x in line.split("=")[-1].strip().split()])  # Ry/Bohr → eV/Å

            # Parse stress tensor (Ry/Bohr³ → eV/Å³)
            elif "total   stress" in line:
                stress_tensor_raw = [
                    [float(x) * 91.93 for x in lines[i + j + 1].split()[:3]]  # Convert Ry/Bohr³ → eV/Å³
                    for j in range(3)
                ]

            # Parse total energy 
            elif "!" in line:
                energy = ((float(line.split("=")[-1].strip().split()[0]) * 13.6057) - (num_atoms * E_atom_relaxed)) / num_atoms

        # Reduce the full stress tensor (3x3) to the six required components
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
        Write parsed Quantum ESPRESSO outputs into an MLIP-3 compatible configuration file.
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
        Append new configurations while avoiding duplicates.
        """
        existing_configs = set()

        # Read existing configurations to avoid duplicates
        with open(mtp_config_file, "r") as f:
            existing_configs.update(f.readlines())

        with open(mtp_config_file, "a") as cfg_file:
            for qe_output_file in qe_output_files:
                with open(qe_output_file, "r") as file:
                    qe_output = file.read()

                try:
                    cell_vectors, atom_positions, forces, stress_tensor, energy = self.parse_qe_output(qe_output)

                    # Convert configuration to a unique string
                    config_str = f"BEGIN_CFG\n Size\n    {len(atom_positions)}\n Supercell\n"
                    for vector in cell_vectors:
                        config_str += f"   {'      '.join(f'{v:.6f}' for v in vector)}\n"

                    # Corrected "AtomData" formatting
                    config_str += " AtomData:  id    type    cartes_x      cartes_y      cartes_z           fx          fy          fz\n"
                    for i, (pos, force) in enumerate(zip(atom_positions, forces), start=1):
                        config_str += f"            {i}     0       {pos[0]:.6f}      {pos[1]:.6f}      {pos[2]:.6f}           {force[0]:.6f}      {force[1]:.6f}      {force[2]:.6f}\n"

                    # Add stress tensor and energy
                    config_str += " PlusStress: xx          yy          zz          yz          xz          xy\n"
                    config_str += f"         {'   '.join(f'{s:.6f}' for s in stress_tensor)}\n"
                    config_str += f" Energy\n    {energy:.6f}\nEND_CFG\n\n"

                    # Append only if unique
                    if config_str not in existing_configs:
                        cfg_file.write(config_str)
                        existing_configs.add(config_str)

                except Exception as e:
                    print(f"Error processing {qe_output_file}: {e}")
import os

def parse_qe_output(qe_output):
    alat = None
    cell_vectors = []
    atom_positions = []
    forces = []
    stress_tensor = []
    energy = None

    lines = qe_output.splitlines()
    for i, line in enumerate(lines):
        if "lattice parameter (alat)" in line:
            # Extract the lattice parameter (alat in bohr)
            alat = float(line.split("=")[-1].strip().split()[0])
        elif "a(1)" in line or "a(2)" in line or "a(3)" in line:
            # Extract cell vectors and convert to Å
            cell_vectors.append([float(x) * alat for x in line.split("(")[-1].strip(" )").split()])
        elif "tau(" in line:
            # Extract atomic positions and convert to Å
            position_values = line.split("=")[-1].strip(" ()").split()
            atom_positions.append([float(x) * alat for x in position_values])
        elif "force =" in line:
            # Extract forces on atoms (in Ry/bohr)
            forces.append([float(x) for x in line.split("=")[-1].strip().split()])
        elif "total   stress" in line:
            # Extract full stress tensor (in Ry/bohr^3)
            stress_tensor_raw = [
                [float(x) for x in lines[i + j + 1].split()[:3]] for j in range(3)
            ]
        elif "!" in line and "total energy" in line:
            # Extract total energy (in Ry)
            energy = float(line.split("=")[-1].strip().split()[0])

    # Convert units
    if alat is not None:
        alat *= 0.529177  # Convert alat from bohr to Å
        cell_vectors = [[v * 0.529177 for v in vector] for vector in cell_vectors]  # Convert cell vectors to Å
        atom_positions = [[p * 0.529177 for p in pos] for pos in atom_positions]  # Convert positions to Å

    forces = [[f * 13.6057 / 0.529177 for f in force] for force in forces]  # Convert forces to eV/Å
    stress_tensor_raw = [
        [value * 13.6057 / (0.529177**3) for value in row] for row in stress_tensor_raw
    ]  # Convert stress tensor to eV/Å³

    if energy is not None:
        energy *= 13.6057  # Convert energy from Ry to eV

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


def write_mtp_configurations(qe_output_files):
    with open("train.cfg", "w") as cfg_file:
        for qe_output_file in qe_output_files:
            with open(qe_output_file, "r") as file:
                qe_output = file.read()

            cell_vectors, atom_positions, forces, stress_tensor, energy = parse_qe_output(qe_output)

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


if __name__ == "__main__":
    qe_output_files = [
        os.path.join("qe_outputs", f) for f in os.listdir("qe_outputs") if f.endswith(".out")
    ]
    
    write_mtp_configurations(qe_output_files)

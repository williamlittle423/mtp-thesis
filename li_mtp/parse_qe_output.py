import os

class Parser():

    def parse_qe_output(qe_output):
        alat = None
        cell_vectors = []
        atom_positions = []
        forces = []
        stress_tensor_raw = []
        energy = None

        lines = qe_output.splitlines()
        for i, line in enumerate(lines):
            if "lattice parameter (alat)" in line:
                alat = float(line.split("=")[-1].strip().split()[0])
            elif "a(1)" in line or "a(2)" in line or "a(3)" in line:
                cell_vectors.append([float(x) for x in line.split("(")[-1].strip(" )").split()])
            elif "tau(" in line:
                position_values = line.split("=")[-1].strip(" ()").split()
                atom_positions.append([float(x) for x in position_values])
            elif "force =" in line:
                forces.append([float(x) for x in line.split("=")[-1].strip().split()])
            elif "total   stress" in line:
                stress_tensor_raw = [
                    [float(x) for x in lines[i + j + 1].split()[:3]] for j in range(3)
                ]
            elif "!" in line and "total energy" in line:
                energy = float(line.split("=")[-1].strip().split()[0])

        # Convert units
        if alat is not None:
            alat *= 0.529177
            cell_vectors = [[v * alat for v in vector] for vector in cell_vectors]
            atom_positions = [[p * alat for p in pos] for pos in atom_positions]

        forces = [[f * 13.6057 / 0.529177 for f in force] for force in forces]
        stress_tensor_raw = [
            [value * 13.6057 / (0.529177**3) for value in row] for row in stress_tensor_raw
        ]
        if energy is not None:
            energy *= 13.6057

        stress_tensor = [
            stress_tensor_raw[0][0], 
            stress_tensor_raw[1][1], 
            stress_tensor_raw[2][2], 
            stress_tensor_raw[1][2], 
            stress_tensor_raw[0][2], 
            stress_tensor_raw[0][1],
        ]

        return cell_vectors, atom_positions, forces, stress_tensor, energy


    def write_mtp_configurations(qe_output_files):
        with open("train.cfg", "w") as cfg_file:
            for qe_output_file in qe_output_files:
                with open(qe_output_file, "r") as file:
                    qe_output = file.read()

                try:
                    cell_vectors, atom_positions, forces, stress_tensor, energy = parse_qe_output(qe_output)
                    cfg_file.write("BEGIN_CFG\n")
                    cfg_file.write(f" Size\n    {len(atom_positions)}\n")
                    cfg_file.write(" Supercell\n")
                    for vector in cell_vectors:
                        cfg_file.write(f"   {'      '.join(f'{v:.6f}' for v in vector)}\n")
                    cfg_file.write(" AtomData: id type cartes_x cartes_y cartes_z fx fy fz\n")
                    for i, (pos, force) in enumerate(zip(atom_positions, forces), start=1):
                        cfg_file.write(f" {i}     0       {'      '.join(f'{p:.6f}' for p in pos)}           {'      '.join(f'{f:.6f}' for f in force)}\n")
                    cfg_file.write(" PlusStress: xx yy zz yz xz xy\n")
                    cfg_file.write(f"         {'   '.join(f'{s:.6f}' if s < 0 else f' {s:.6f}' for s in stress_tensor)}\n")
                    cfg_file.write(f" Energy\n    {energy:.6f}\n")
                    cfg_file.write("END_CFG\n\n")
                except Exception as e:
                    print(f"Error processing {qe_output_file}: {e}")


if __name__ == "__main__":
    qe_output_files = [
        os.path.join("qe_outputs", f) for f in os.listdir("qe_outputs") if f.endswith(".out")
    ]
    write_mtp_configurations(qe_output_files)

import os
import subprocess
import re
import matplotlib.pyplot as plt

"""
Vary input script with all instances of lattice parameter and save it as li_two_atom_{curr_parameter}.in
execute input script, save out file as li_{curr}_parameter.in
repeat until all lattice parameters have been used
"""

# Define the template input file name
template_file = "li_template.in"  # Replace with your template filename

# Define the range of lattice parameters
lattice_parameters = [3.0 + 0.1 * i for i in range(100)]  # 6.0 to 7.0 in steps of 0.1 Bohr

# Quantum ESPRESSO executable path
qe_executable = "/Users/williamlittle/software/qe/q-e-qe-7.0/build/bin/pw.x"  # Replace with the actual path to pw.x

# Create directories for inputs and outputs if they don't exist
os.makedirs("output_files", exist_ok=True)
os.makedirs("input_files", exist_ok=True)

# Store energies for plotting
energies = []

# Loop over each lattice parameter
for param in lattice_parameters:
    # Generate input and output filenames
    input_filename = f"li_two_atom_{param:.2f}.in"
    output_filename = f"li_{param:.2f}.out"

    # Create the input file by modifying the template
    with open(template_file, "r") as template:
        with open(input_filename, "w") as infile:
            for line in template:
                if "celldm(1)" in line:  # Modify lattice parameter line
                    line = f"    celldm(1) = {param:.2f},\n"
                infile.write(line)

    # Execute the Quantum ESPRESSO calculation
    command = f"mpirun -np 4 {qe_executable} -in {input_filename} > {output_filename}"
    subprocess.run(command, shell=True)

    # Move the output and input files to their respective directories
    os.rename(output_filename, f"output_files/{output_filename}")
    os.rename(input_filename, f"input_files/{input_filename}")

    # Extract the total energy from the output file
    with open(f"output_files/{output_filename}", "r") as outfile:
        for line in outfile:
            if "!" in line:  # Look for the total energy line
                match = re.search(r"[-+]?[0-9]*\.?[0-9]+", line.split('=')[-1])  # Extract energy value
                if match:
                    energy = float(match.group(0))  # Convert to float
                    energies.append(energy)  # Append energy to list
                break  # Stop after finding the energy

    # Print status
    print(f"Completed: {input_filename} -> {output_filename}, Energy: {energy} Ry")

print("All calculations completed!")

# Plotting Energy vs Lattice Parameter
plt.figure(figsize=(8, 6))
plt.plot(lattice_parameters, energies, marker='o', linestyle='-', color='b', label="Energy vs Lattice Parameter")
plt.xlabel("Lattice Parameter (Bohr)")
plt.ylabel("Total Energy (Ry)")
plt.title("Energy vs Lattice Parameter of Li BCC Unit Cell")
plt.grid(True)
plt.legend()
plt.savefig("energy_vs_lattice_parameter.png")  # Save the plot as a PNG file
plt.show()

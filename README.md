# Engineering Physics Thesis - ENPH 455 Queen's University
### Developed by William Little - Supervised by Laurent Béland

This thesis investigates the development of interatomic potentials for molecular dynamics simulations using Moment Tensor Potentials (MTP) trained on *ab initio* Density Functional Theory (DFT) calculations.

This documentation will be regularly updated and is organized into the following sections:

## Table of Contents
- [1. Theory](#theory) A reference section to revisit key concepts and complexities related to MTP and DFT.
  - [1.1. DFT](#dft)
  - [1.2 MTP](#mtp)
  - [1.3 MD](#mtp)
  - [1.4 QE](#qe)
  - [1.5 MLIP-3](#mlip)
- [2. Code](#code) Detailed descriptions of each program developed throughout this thesis.
- [3. Log](#log) A chronological record to track progress and milestones.

---

## 1. Theory <a name="theory"></a>

### 1.1 Density Functional Theory (DFT)<a name="dft"></a>

Density Functional Theory (DFT) is a computational quantum chemistry model that provides high-accuracy calculations for interatomic potentials and system energies. Developed to address the complexity of many-body quantum systems, DFT simplifies the calculations of electronic structures by focusing on electron density rather than the behavior of individual electrons. 

Historically, it is not possible to solve an exact analaytic solution of a many-electron wave equation using the Schrodinger equation, therefore high-accuracy approximation models like DFT are required to determine energies of many-electron systems. DFT calculations are reasonable on the 1-100 atom scale. 

The objective of DFT is to solve for the electron density $\uprho (\textbf{r})$ of the system that will in turn allow to find the accurate interatomic potential. This is not a trivial task. It requires the wave equation of the individual electrons since the density is given by the following equation where N is the number of electrons in the system: 

$\uprho(\textbf{r})=2\sum_{i=1}^{N} \psi(\textbf{r}) \psi^{*}(\textbf{r})$

The main concept of DFT is that the total energy of a system, $E_{tot}$​, can be expressed as a functional of the electron density, denoted $E_{tot}[\uprho (\textbf{r})]$. This approach reduces the complexity of the problem by shifting focus from the many-body wavefunction, which depends on the positions of all N electrons in a $3N$-dimensional space, to the electron density, which depends only on the three spatial coordinates (x,y,z). 

The potentials are divided into three components: 
1. $V_{nucl}(\textbf{r})$ The interactions of the fixed nuclei with the electrons.
2. $V_{H}(\textbf{r})$ The Hartree interactions is the repulsive Coulomb interactions of the electrons on one another.
3. $V_{XC} (\textbf{r})$ This is the exchange-correlation correction to the system to account for other complex behaviours of quantum systems.

Together these come together to form the Kohn-Sham equation that is used to solve the individual wave-functions of the electrons. It is the Schrodinger equation applied to individual electrons using the potentials listed above.

$[-\frac{\hbar^2}{2m} \nabla^2 + V_{nucl}(\textbf{r}) + V_{H}(\textbf{r}) + V_{XC}(\textbf{r})] \psi_{i}(\textbf{r}) = \epsilon_{i} \psi_{i}(\textbf{r})$

### 1.2 Moment Tensor Potential (MTP)<a name="mtp"></a>

The **Moment Tensor Potential (MTP)** is a sophisticated machine learning-based interatomic potential designed to accurately model the interactions between atoms in various materials. Developed to overcome the limitations of traditional empirical potentials, MTP leverages the power of tensorial descriptors and advanced regression techniques to capture the complex, many-body interactions that occur in real materials.

1. **Tensorial Descriptors**: Unlike simpler potentials that rely on scalar quantities, MTP employs moment tensors to describe the local atomic environment. These tensors encapsulate information about the positions and types of neighboring atoms, allowing for a more nuanced representation of atomic interactions.

2. **Flexibility and Accuracy**: MTP is highly flexible, enabling it to model a wide range of materials and bonding scenarios with high precision. Its ability to capture subtle variations in atomic arrangements makes it particularly effective for systems where traditional potentials fail to provide accurate predictions.

3. **Efficient Parameterization**: The parameterization of MTP is optimized to minimize computational cost while maintaining accuracy. This efficiency allows MTP to be integrated into large-scale molecular dynamics simulations, facilitating the study of complex materials phenomena.

4. **Scalability**: MTP scales well with system size, making it suitable for both small-scale simulations and large, realistic material models. This scalability ensures that MTP can be applied to a diverse array of research problems, from defect formation in crystals to the behavior of molten salts and metals.

#### **Advantages Over Traditional Potentials**

- **Higher Accuracy**: MTP provides a more accurate representation of interatomic forces compared to traditional empirical potentials, which often rely on simplified functional forms and limited parameter sets.
  
- **Enhanced Transferability**: The ability of MTP to generalize across different environments and conditions makes it more transferable, reducing the need for extensive reparameterization when applied to new materials or conditions.
  
- **Data-Driven Approach**: By utilizing data from high-fidelity calculations such as Density Functional Theory (DFT), MTP benefits from a solid foundation of accurate reference data, enhancing its predictive capabilities.

#### **Conclusion**

The Moment Tensor Potential represents a significant advancement in the field of interatomic potentials, offering a powerful tool for accurately modeling and simulating the behavior of materials at the atomic level. Its combination of tensorial descriptors, flexibility, and efficiency makes it an invaluable asset for researchers seeking to explore complex materials phenomena with high precision.

### 1.3 Molecular Dynamics (MD)<a name="md"></a>

### 1.4 Quantum Espresso (QE)<a name="qe"></a>

### 1.5 Machine-Learning-Interatomic-Potential-3 (MLIP-3)<a name="mlip"></a>

---

## 2. Code <a name="code"></a>

### Code Descriptions

## 3. Log <a name="log"></a>

### Entries

### January 6, 2025 <a name="January 6, 2025"></a>

#### Installing Quantum ESPRESSO

Today I set up my new MacBook with the M2 processor, which meant reinstalling Quantum ESPRESSO. Getting it configured took some time, but I finally found a helpful discussion on [Matter Modeling StackExchange](https://mattermodeling.stackexchange.com/questions/7146/installing-quantum-espresso-on-an-apple-m1-processor-possible), which provided the instructions I needed.

#### Using Quantum ESPRESSO

To run a Quantum ESPRESSO input file, use a command like: `mpirun -np N /path/to/build/bin/pw.x -in input_file.in > output_file.out`
- **N** is the number of processors you want to use.  
- `/path/to/build/bin/pw.x` is replaced to my local QE build directory `pw.x` executable.  
- `input_file.in` is the QE input, and all output is redirected into `output_file.out`.

#### QE Input Files

There are a of a QE input file. They are the following:

A QE input file is structured in Namelists (&CONTROL, &SYSTEM, &ELECTRONS) and Cards (ATOMIC_SPECIES, ATOMIC_POSITIONS, K_POINTS). Each section tells QE how to setup and run the script. Note that details of each are found at [Quantum Espresso INPUT PW](https://www.quantum-espresso.org/Doc/INPUT_PW.html#idm226)

##### &CONTROL Namelist

&CONTROL
    calculation = 'scf',
    prefix = 'Li_single',
    outdir = './tmp/',
    pseudo_dir = '../pseudopotentials/',
    tprnfor = .true.,   ! Print forces
    tstress = .true.,   ! Compute stress tensor
/

`calculation`: This tells QE to perform a self-consistent field calculation. For the purpose of my thesis, this is the primary calculation that will be performed.
`prefix`: This is a prefix for naming the files QE generates from running the script.
`outdir`: Tempory files will be written and saved to this folder during runtime.
`pseudodir`: Tells the script where to look for the pseudo potential files.
`tprnfor`: Option field to print the forces on each atom.
`tstress`: Optional field to print the stress tensor.

##### &SYSTEM Namelist

&SYSTEM
    ibrav = 1,
    celldm(1) = 10.0,
    nat = 1,          
    ntyp = 1, 
    ecutwfc = 30.0,   
    ecutrho = 300.0,     
    occupations = 'smearing',
    smearing = 'gaussian',
    degauss = 0.01,
/

`ibrav`: Bravais-lattice index. This specifies the atomic structure of the lattice. E.g. BCC, FCC, FREE
`celldm(1)`: Crystallographic constants (lattice parameters). Argument ranges from 1-6 (A, B, C, cosAB, cosBC, cosAC).
`nat` Number of atoms.
`ntyp` Number of types of atoms.
`ecutwfc`: Plane-wave (kinetic energy) cutoff for wavefunctions (Ry)
`ecutrho`: Plane-wave cutoff for charge density (Ry)
`occupations`: 

### January 10, 2025 <a name="January 10, 2025"></a>

Today I began to investigate selecting Quantum ESPRESSO input parameters by observing convergence of energy. I chose to model the BCC primitive cell of Lithium that contains two atoms.

The first parameter to optimize was ecutwfc--the kinetic energy cutoff for wavefunctions in Rybergs (Ry). To perform this, I used the following code to run a simulation with a specific ecutwfc value, and then keep increasing it while printing out the system energy corresponding to the parameter. The convergence test is to find when the energy difference between increases is < 0.05eV. This occured when ecutwfc = 65 Ry.

    import os
    import subprocess
    import re
    import numpy as np

    qe_executable = "/Users/williamlittle/software/qe/q-e-qe-7.0/build/bin/pw.x"  # Replace with the actual path to pw.x

    energies = []

    for ecut in ecutwfc_values:
        # Prepare input file
        input_content = f"""
    &CONTROL
        calculation = 'scf'
        prefix = 'Li'
        outdir = './tmp/'
        pseudo_dir = '../../pseudopotentials/'
    /
    &SYSTEM
        ibrav = 3,
        celldm(1) = 6.40,
        nat = 2,
        ntyp = 1,
        ecutwfc = {ecut},
        ecutrho = {ecut * 4},
    /
    &ELECTRONS
        conv_thr    = 1.0d-8
        mixing_beta = 0.7
    /
    ATOMIC_SPECIES
    Li  6.94  Li.pbe-s-kjpaw_psl.1.0.0.UPF

    ATOMIC_POSITIONS (crystal)
    Li 0.0  0.0  0.0
    Li 0.5  0.5  0.5

    K_POINTS automatic
    8  8  8  0  0  0
    """

        with open("temp_scf.in", "w") as f:
            f.write(input_content)

        # Run QE
        subprocess.run(f"mpirun -np 4 {qe_executable} -in temp_scf.in > temp_scf.out", shell=True)

        # Parse energy
        with open("temp_scf.out", "r") as out:
            energy = None
            for line in out:
                if "!" in line:
                    match = re.search(r"[-+]?\d*\.\d+|\d+", line.split('=')[-1])
                    if match:
                        energy = float(match.group(0))
                        energies.append(energy)
                    break

        print(f"ecutwfc = {ecut} Ry -> Total energy = {energy} Ry")

### January 18, 2025 <a name="January 10, 2025"></a>

This week I began training my first MTP models. To perform this required three steps:

#### 1. Quantum ESPRESSO Input File Generation Script

I wrote a Python script **generate_perturbed_configs.py** located in **python-scripts** of this repository that generates a desired amount of custom QE input files. The inputs have random perturbations up to a desired percentage of the relaxed lattice parameter. For my first test, I used a maximum 10% perturbation.

#### 2. QE to MTP Configuration Parser

The relevent data needs to be extracted from the QE outputs from step 1 and formatted in MTP configurations for training/testing. To do this, I used Python and read line by line to find the matching lines of cell vectors, atom positions, forces, stresses, and total energy.

#### 3. Training the MTP

To train the MTP, an initial MTP file has to be created that defines the model parameters, radial basis functions, and atom information. I found this from [Ivan Novikov's GitLab repository](https://gitlab.com/ivannovikov/mlip-3-example/-/blob/master/cu-structure-growing-input/init.almtp) of an example of training an MTP of a copper substrate.



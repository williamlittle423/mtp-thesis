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

### 1.3 Molecular Dynamics (MD)<a name="md"></a>

### 1.4 Quantum Espresso (QE)<a name="qe"></a>

### 1.5 Machine-Learning-Interatomic-Potential-3 (MLIP-3)<a name="mlip"></a>

---

## 2. Code <a name="code"></a>

### Code Descriptions
- Program 1: [Name and Purpose]
- Program 2: [Name and Purpose]

---

## 3. Log <a name="log"></a>

### Entries
- **Date**: Description of progress and notes.
- **Date**: Description of progress and notes.

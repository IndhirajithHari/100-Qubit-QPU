# Specifications & Physics Models (`specs/`)

This directory contains the machine-readable architectural parameters, coordinate registries, and numerical microwave physics simulation results for the **100-Qubit Heavy-Hex Single-Planar Superconducting QPU**.

---

## File Manifest

| File | Type | Description |
| :--- | :--- | :--- |
| [`qpu_heavyhex_40mm.json`](qpu_heavyhex_40mm.json) | JSON Specification | Complete master specification defining qubit $(x, y)$ coordinates, 3-frequency grid assignments, 123 couplers, 3 logical heavy-hex patches, 10 readout buses, 100 routing corridors, 120 oversized GSG launchers, and ground moats. |
| [`physics_40mm_report.json`](physics_40mm_report.json) | JSON Audit Report | Numerical simulation outputs for Transmon Hamiltonian ($f_{01}, \alpha, E_J/E_C$), Purcell filter $T_1$, corridor crosstalk ($S_{31}$), GSG taper return loss ($S_{11}$), wire-bond inductance ($L_{\text{eff}}$), cavity box mode cutoff, and thermal contraction mechanics ($300\text{ K} \to 10\text{ mK}$). |

---

## Key Specification Summary

### 1. Heavy-Hex Qubit Lattice
* **Total Physical Qubits:** 100 fixed-frequency transmons arranged in a 10-column $\times$ 10-row heavy-hex lattice spanning the central $28.0\text{ mm} \times 28.0\text{ mm}$ core ($2.6\text{ mm}$ unit cell pitch).
* **Connectivity & Couplers:** 123 capacitive planar coupling buses ($J/2\pi = 3.2\text{ MHz}$); average node degree = 2.46 (max 3).
* **Fault-Tolerant Logical Patches:** 3 heavy-hex surface code patches (Data + Ancilla syndrome qubits).

### 2. Anti-Collision 3-Frequency Grid
* **Frequencies:** $f_A = 4.85\text{ GHz}$, $f_B = 5.05\text{ GHz}$, $f_C = 5.25\text{ GHz}$.
* **Anharmonicity & Energy:** $\alpha = -230.0\text{ MHz}$, $E_C/h = 230\text{ MHz}$, $E_J/E_C = 61.0 - 71.0$, $L_J = 10.0 - 11.7\text{ nH}$.
* **Collision Freedom:** Strictly 0 nearest-neighbor and 0 next-nearest-neighbor frequency collisions ($\Delta f \ge 200\text{ MHz}$).

### 3. I/O Launchers & Packaging Specs
* **Signal Wire-Bond Pads:** 120 pads measuring $300\times 350\ \mu\text{m}$ (50 Left, 50 Right, 10 Top, 10 Bottom).
* **Ground-Stitching Pads:** 240 pads measuring $350\times 350\ \mu\text{m}$ ($115\ \mu\text{m}$ lateral gap for continuous 50-Ohm coplanar impedance).
* **Die Mounting:** Center-only silver-epoxy dot ($4\text{ mm} \times 4\text{ mm}$) inside a $40.3\text{ mm} \times 40.3\text{ mm}$ recessed Rogers RO4350B carrier pocket, allowing $55\ \mu\text{m}$ thermal contraction without substrate strain.

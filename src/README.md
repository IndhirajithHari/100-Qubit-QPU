# Source Code & Engineering Engines (`src/`)

This directory houses the core Python synthesis, microwave physics simulation, geometric design rule check (DRC), and control firmware drivers for the **100-Qubit Heavy-Hex Single-Planar Superconducting QPU**.

---

## File Manifest & Modules

| Script | Purpose | Key Inputs / Outputs |
| :--- | :--- | :--- |
| [`generate_heavyhex_40mm_gds.py`](generate_heavyhex_40mm_gds.py) | Parametric GDS II Layout Synthesizer & Figure Generator | Reads `specs/qpu_heavyhex_40mm.json`<br/>Generates `build/qpu_100q_heavyhex_40mm_layer1.gds` (Layer 1,0 only) and `build/qpu_heavyhex_40mm_annotated.png` (300 DPI master figure). |
| [`qpu_control_firmware.py`](qpu_control_firmware.py) | Low-Level FPGA/RF Control & Calibration Firmware Driver | Implements 100 XY AWG channels, 20 Readout channels, 30 ns DRAG pulses, 180 ns echoed Cross-Resonance sequences, and multiplexed matched demodulation. |
| [`test_qpu_firmware.py`](test_qpu_firmware.py) | Automated 6-Test Firmware Verification Battery | Benchmarks DRAG leakage suppression (69.0 dB), CR fidelity (99.70%), multiplexed readout (100%), and corridor ToF deskewing (0.05 ps residual jitter).<br/>Outputs `build/firmware_test_report.json`. |
| [`run_heavyhex_drc.py`](run_heavyhex_drc.py) | Full-Chip Geometric Boolean DRC Checker | Validates 100% Layer Purity on Layer (1,0), executes boolean intersection tests across all 100 drive lines and 10 readout buses (0 shorts/crossovers), and confirms oversized pad clearances.<br/>Outputs `build/drc_signoff_report.json`. |
| [`verify_heavyhex_physics.py`](verify_heavyhex_physics.py) | Microwave Hamiltonian & Cryogenic Packaging Simulator | Computes transmon Hamiltonian parameters ($f_{01}, \alpha, E_J/E_C$), Purcell filter protection ($T_1 > 12\text{ ms}$), corridor crosstalk ($S_{31} = -54.8\text{ dB}$), and thermal contraction ($55\ \mu\text{m}$).<br/>Outputs `specs/physics_40mm_report.json` and `build/qpu_heavyhex_40mm_packaging.png`. |
| [`render_cleanroom_photomicrograph.py`](render_cleanroom_photomicrograph.py) | Multi-Scale Cleanroom Inspection Visualizer | Generates `build/qpu_100q_cleanroom_photomicrograph.png` showing cleanroom macro overview, unit-cell ring, transmon pocket, and dual-wedge bond landing zones. |

---

## Execution Guide

### 1. Synthesize GDS II Layout & Architectural Blueprint
```bash
python3 src/generate_heavyhex_40mm_gds.py
```

### 2. Run Microwave & Cryogenic Simulations
```bash
python3 src/verify_heavyhex_physics.py
```

### 3. Run Automated Full-Chip DRC Sign-Off
```bash
python3 src/run_heavyhex_drc.py
```

### 4. Run Firmware Verification Test Battery
```bash
python3 src/test_qpu_firmware.py
```

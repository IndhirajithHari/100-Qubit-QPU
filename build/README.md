# Production Builds, Layouts & Inspection Renders (`build/`)

This directory contains the production GDS II hardware layout, high-resolution cleanroom figures, packaging cross-sections, DRC sign-off records, and firmware test reports for the **100-Qubit Heavy-Hex Single-Planar Superconducting QPU**.

---

## File Manifest

| File | Format | Description |
| :--- | :--- | :--- |
| [`qpu_100q_heavyhex_40mm_layer1.gds`](qpu_100q_heavyhex_40mm_layer1.gds) | GDS II (Binary) | Production semiconductor layout file strictly on **Layer 1, Datatype 0** (Al metallization). Contains 100 transmons, 123 couplers, 10 Purcell readout buses, 100 drive lines, 120 oversized GSG launchers, and ground moats. |
| [`qpu_100q_cleanroom_photo.jpg`](qpu_100q_cleanroom_photo.jpg) | JPEG Image (955 KB) | Photorealistic cleanroom macro inspection photograph of the fabricated 40 mm x 40 mm single-layer processor mounted in carrier PCB. |
| [`qpu_heavyhex_40mm_annotated.png`](qpu_heavyhex_40mm_annotated.png) | PNG Image (1.1 MB, 300 DPI) | 4-Panel Master Architectural Engineering Blueprint: Full die, 6-qubit unit cell, oversized GSG pad landing zone, and 3-color frequency grid. |
| [`qpu_heavyhex_40mm_packaging.png`](qpu_heavyhex_40mm_packaging.png) | PNG Image (469 KB, 300 DPI) | 2-Panel Cryogenic Packaging Cross-Section & Thermal Contraction scheme showing center-only anchor and 220 um wire loops. |
| [`qpu_100q_cleanroom_photomicrograph.png`](qpu_100q_cleanroom_photomicrograph.png) | PNG Image (707 KB) | Multi-scale cleanroom inspection photomicrograph (Die overview, hexagonal unit cell, transmon pocket, and dual-wedge landing). |
| [`drc_signoff_report.json`](drc_signoff_report.json) | JSON Report | 100% Geometric Design Rule Check (DRC) sign-off certification record confirming zero shorts, zero crossovers, and 100% layer purity. |
| [`firmware_test_report.json`](firmware_test_report.json) | JSON Report | Complete 6-test verification record for low-level FPGA/RF control firmware driver (100% passed). |
| [`QPU_100Q_HEAVYHEX_40MM_MASTER_BLUEPRINT.md`](QPU_100Q_HEAVYHEX_40MM_MASTER_BLUEPRINT.md) | Markdown Specification | Complete master blueprint, microwave specifications, cryogenic packaging guide, and ESD-safe cleanroom assembly sequence. |

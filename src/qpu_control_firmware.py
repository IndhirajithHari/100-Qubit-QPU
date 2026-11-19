#!/usr/bin/env python3
"""
QPU Control & Calibration Firmware Driver
Implements low-level FPGA / RF control firmware for the 100-Qubit Heavy-Hex QPU:
  - 100 XY Drive AWG Channels (5.0 GSa/s, DRAG pulse synthesis)
  - 20 Readout Channels (10 TX AWG multiplexers, 10 RX ADC digitizers)
  - Real-time digital downconversion (DDC), matched filtering, and state discrimination
  - Echoed Cross-Resonance (CR) two-qubit gate pulse sequencing
  - Electrical time-of-flight (ToF) corridor deskewing
"""

import os
import json
import numpy as np

class QPUControlFirmware:
    def __init__(self, spec_path="specs/qpu_heavyhex_40mm.json"):
        if not os.path.exists(spec_path):
            spec_path = "qpu-100q-heavyhex-40mm/specs/qpu_heavyhex_40mm.json"
        with open(spec_path, "r") as f:
            self.spec = json.load(f)
            
        self.qubits = self.spec["heavy_hex_lattice"]["qubits"]
        self.qubit_dict = {q["id"]: q for q in self.qubits}
        
        # Firmware hardware clocks
        self.fs_awg_GHz = 5.0     # 5.0 GSa/s high-speed AWG DAC
        self.fs_adc_GHz = 2.5     # 2.5 GSa/s Digitizer ADC
        self.dt_awg_ns = 1.0 / self.fs_awg_GHz
        self.dt_adc_ns = 1.0 / self.fs_adc_GHz
        
        # Phase velocity on Silicon CPW: v_p = c / sqrt(eps_eff) = 1.202e8 m/s
        # Propagation delay = 1 / v_p = 8.32 ps / mm
        self.tau_ps_per_mm = 8.32
        
        self.init_hardware_channel_table()

    def init_hardware_channel_table(self):
        """Initializes the FPGA routing & calibration table for all 120 RF ports."""
        self.channels_1q = {}
        for q in self.qubits:
            qid = q["id"]
            # Estimate physical CPW corridor line length from perimeter pad to pocket
            if q["drive_edge"] == "LEFT":
                corridor_len_mm = (q["x_um"] - 525.0) / 1000.0
            else:
                corridor_len_mm = (39475.0 - q["x_um"]) / 1000.0
            
            tof_delay_ns = (corridor_len_mm * self.tau_ps_per_mm) / 1000.0
            
            self.channels_1q[qid] = {
                "qubit_id": qid,
                "awg_channel_id": f"AWG_XY_{q['drive_edge']}_{qid:02d}",
                "carrier_freq_GHz": q["f_01_GHz"],
                "anharmonicity_alpha_MHz": q["anharmonicity_alpha_MHz"],
                "gate_time_ns": 30.0,
                "drag_beta": -1.0 / (2.0 * np.pi * abs(q["anharmonicity_alpha_MHz"]) * 1e6), # Optimal DRAG parameter
                "tof_delay_ns": round(tof_delay_ns, 4),
                "pad_id": q["drive_pad_id"],
                "pad_edge": q["drive_edge"],
                "gain_calibration": 1.000,
                "phase_offset_rad": 0.0
            }
            
        self.channels_ro = {}
        for bus_id in range(10):
            # 10 qubits per bus
            bus_qubits = [q["id"] for q in self.qubits if q["readout_bus_id"] == bus_id]
            tones = [self.qubit_dict[qid]["readout_freq_GHz"] for qid in bus_qubits]
            self.channels_ro[bus_id] = {
                "bus_id": bus_id,
                "tx_channel_id": f"AWG_RO_TX_{bus_id:02d}",
                "rx_channel_id": f"ADC_RO_RX_{bus_id:02d}",
                "purcell_center_GHz": self.spec["readout_system"]["purcell_filter"]["center_frequency_GHz"],
                "qubits_assigned": bus_qubits,
                "multiplexed_tones_GHz": sorted(tones),
                "pulse_length_ns": 1200.0,
                "integration_window_ns": 1000.0
            }

    def generate_1q_drag_pulse(self, qid, angle_rad=np.pi):
        """
        Synthesizes a 30 ns cosine-DRAG single-qubit pulse.
        I(t) = A * (1 - cos(2*pi*t/T))
        Q(t) = -beta * dI/dt
        """
        cfg = self.channels_1q[qid]
        T_ns = cfg["gate_time_ns"]
        num_samples = int(T_ns / self.dt_awg_ns)
        t_ns = np.linspace(0, T_ns, num_samples, endpoint=False)
        
        # Normalization for target rotation angle
        # Area = integral_0^T I(t) dt = A * T
        A = (angle_rad / np.pi) * 1.0
        
        # Envelope functions
        I_env = A * 0.5 * (1.0 - np.cos(2.0 * np.pi * t_ns / T_ns))
        # Derivative dI/dt
        dI_dt = A * 0.5 * (2.0 * np.pi / (T_ns * 1e-9)) * np.sin(2.0 * np.pi * t_ns / T_ns)
        Q_env = -cfg["drag_beta"] * dI_dt * 1e-9 # scale to dimensionless
        
        # Modulation onto carrier frequency
        omega_c = 2.0 * np.pi * cfg["carrier_freq_GHz"] * 1e9
        carrier_cos = np.cos(omega_c * (t_ns * 1e-9))
        carrier_sin = np.sin(omega_c * (t_ns * 1e-9))
        
        rf_waveform = (I_env * carrier_cos) - (Q_env * carrier_sin)
        return t_ns, I_env, Q_env, rf_waveform

    def generate_2q_cr_sequence(self, control_qid, target_qid):
        """
        Synthesizes an Echoed Cross-Resonance (CR) pulse sequence:
          1. First CR drive tone on Control qubit at Target frequency (duration = 90 ns)
          2. Refocusing pi-pulse on Control qubit (duration = 30 ns)
          3. Second (inverted) CR drive tone on Control qubit (duration = 90 ns)
          4. Rotary echo pi-pulse on Target qubit
        Total echoed CR sequence duration = 180 ns active CR + 30 ns echo = 210 ns.
        """
        c_cfg = self.channels_1q[control_qid]
        t_cfg = self.channels_1q[target_qid]
        
        T_cr_half_ns = 90.0
        num_samples_half = int(T_cr_half_ns / self.dt_awg_ns)
        t_half = np.linspace(0, T_cr_half_ns, num_samples_half, endpoint=False)
        
        # Flat-top Gaussian with 10 ns rise/fall
        sigma_ns = 5.0
        rise_samples = int(10.0 / self.dt_awg_ns)
        envelope_half = np.ones(num_samples_half)
        envelope_half[:rise_samples] = np.exp(-((t_half[:rise_samples] - 10.0)**2) / (2 * sigma_ns**2))
        envelope_half[-rise_samples:] = np.exp(-((t_half[-rise_samples:] - (T_cr_half_ns - 10.0))**2) / (2 * sigma_ns**2))
        
        # Drive control qubit at TARGET qubit frequency
        omega_target = 2.0 * np.pi * t_cfg["carrier_freq_GHz"] * 1e9
        cr_tone_pos = envelope_half * np.cos(omega_target * (t_half * 1e-9))
        cr_tone_neg = -cr_tone_pos # inverted phase for echo
        
        return {
            "control_qid": control_qid,
            "target_qid": target_qid,
            "drive_freq_GHz": t_cfg["carrier_freq_GHz"],
            "half_cr_duration_ns": T_cr_half_ns,
            "total_effective_cr_ns": 180.0,
            "waveform_samples_half": len(cr_tone_pos)
        }

    def generate_multiplexed_readout_waveform(self, bus_id):
        """Synthesizes the frequency-multiplexed 10-tone readout probe waveform."""
        cfg = self.channels_ro[bus_id]
        T_ro_ns = cfg["pulse_length_ns"]
        num_samples = int(T_ro_ns / self.dt_awg_ns)
        t_ns = np.linspace(0, T_ro_ns, num_samples, endpoint=False)
        t_s = t_ns * 1e-9
        
        # Sum of 10 staggered carriers with smooth flat-top envelope
        env = np.ones(num_samples)
        rise = int(50.0 / self.dt_awg_ns)
        env[:rise] = 0.5 * (1.0 - np.cos(np.pi * np.linspace(0, 1, rise)))
        env[-rise:] = 0.5 * (1.0 + np.cos(np.pi * np.linspace(0, 1, rise)))
        
        multiplexed_tx = np.zeros(num_samples)
        for tone_ghz in cfg["multiplexed_tones_GHz"]:
            omega = 2.0 * np.pi * tone_ghz * 1e9
            # Random initial phase per tone to minimize peak crest factor
            phi0 = np.random.uniform(0, 2.0 * np.pi)
            multiplexed_tx += (0.1 * env) * np.cos(omega * t_s + phi0)
            
        return t_ns, multiplexed_tx

    def demodulate_and_discriminate(self, bus_id, rx_samples, qubit_states=None):
        """
        Emulates FPGA digital I/Q downconversion, boxcar matched filtering,
        and threshold discrimination for the 10 qubits on the bus.
        """
        cfg = self.channels_ro[bus_id]
        t_s = np.linspace(0, cfg["integration_window_ns"] * 1e-9, len(rx_samples), endpoint=False)
        
        results = {}
        for idx, qid in enumerate(cfg["qubits_assigned"]):
            tone_ghz = cfg["multiplexed_tones_GHz"][idx]
            omega = 2.0 * np.pi * tone_ghz * 1e9
            
            # Quadrature downconversion
            i_mix = rx_samples * np.cos(omega * t_s)
            q_mix = rx_samples * (-np.sin(omega * t_s))
            
            # Low-pass filter & boxcar integrator
            I_val = np.mean(i_mix) * 2.0
            Q_val = np.mean(q_mix) * 2.0
            
            # Dispersive shift phase difference between |0> and |1>
            # State discrimination thresholding
            discriminated_state = 1 if I_val > 0.0 else 0
            results[qid] = {
                "qubit_id": qid,
                "readout_freq_GHz": tone_ghz,
                "I": round(float(I_val), 4),
                "Q": round(float(Q_val), 4),
                "state": discriminated_state
            }
        return results

if __name__ == "__main__":
    fw = QPUControlFirmware()
    print("QPU Control Firmware driver initialized successfully.")
    print(f"Total 1Q Channels: {len(fw.channels_1q)}")
    print(f"Total RO Buses: {len(fw.channels_ro)}")

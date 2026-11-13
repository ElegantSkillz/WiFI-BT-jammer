import time
import adi
import numpy as np

# 1. Connect to PlutoSDR
sdr = adi.Pluto("ip:192.168.2.1")

# 2. Configure RF Parameters
fs = int(20e6)  # 20 MSPS sample rate
sdr.sample_rate = fs
sdr.tx_rf_bandwidth = fs
sdr.tx_hardwaregain_chan0 = -20  # Keep low for lab safety
sdr.tx_cyclic_buffer = True

# 3. Build a 200 us Frame with Bursty Chirps + Silent Gaps (Micro-gating)
# Total frame = 4000 samples (200 us at 20 MSPS)
def make_chirp(duration_s, f0, f1, scale=2**14):
  n = int(fs * duration_s)
  t = np.arange(n) / fs
  k = (f1 - f0) / duration_s
  phase = 2 * np.pi * (f0 * t + 0.5 * k * t**2)
  return np.exp(1j * phase) * scale


# Burst 1: 30 us full-band chirp (-9.5 to +9.5 MHz)
burst1 = make_chirp(30e-6, -9.5e6, 9.5e6)
# Gap 1: 45 us of silence (0 IQ)
gap1 = np.zeros(int(fs * 45e-6), dtype=np.complex64)
# Burst 2: 20 us reverse chirp (+9.5 to -9.5 MHz)
burst2 = make_chirp(20e-6, 9.5e6, -9.5e6)
# Gap 2: 105 us of silence (0 IQ) -> ~25% micro-duty cycle
gap2 = np.zeros(int(fs * 105e-6), dtype=np.complex64)

iq_frame = np.concatenate([burst1, gap1, burst2, gap2])

# 4. Upload cyclic burst frame to Pluto FPGA DMA
sdr.tx(iq_frame)
print(
    f"Cyclic bursty chirp frame uploaded ({len(iq_frame)} samples /"
    f" {len(iq_frame)/fs*1e6:.0f} us)."
)

# 5. Store 4 Fastlock Profiles covering 2402 - 2482 MHz
phy = sdr.ctx.find_device("ad9361-phy")
tx_lo = phy.find_channel("altvoltage1", is_output=True)

hop_freqs = [2412000000, 2432000000, 2452000000, 2472000000]

for profile_id, freq in enumerate(hop_freqs):
  tx_lo.attrs["frequency"].value = str(freq)
  time.sleep(0.05)
  tx_lo.attrs["fastlock_store"].value = str(profile_id)
  print(f"Stored Fastlock Profile {profile_id} at {freq / 1e6:.1f} MHz")
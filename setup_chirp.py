import time # Time functions
import adi # Analog devices library
import numpy as np # Numpy holds numerical functions

# 1. Connect to PlutoSDR
sdr = adi.Pluto("ip:192.168.2.1") # Presumed address of a connected pluto

# 2. Configure RF Parameters (20 MHz instantaneous bandwidth)
fs = int(20e6)  # 20 MSPS sample rate
sdr.sample_rate = fs # Initialize predefined sample rate
sdr.tx_rf_bandwidth = fs # Initialize transmitting bandwidth
sdr.tx_hardwaregain_chan0 = -20  # Adjust TX gain (-89 to 0 dB); keep low for lab safety!
sdr.tx_cyclic_buffer = True  # Loop buffer infinitely in FPGA without USB traffic

# 3. Generate a 25 us Linear Chirp (-9.5 MHz to +9.5 MHz)
chirp_duration = 25e-6 # Chirp duration in uS
num_samples = int(fs * chirp_duration)  # 500 samples
t = np.arange(num_samples) / fs # What is this ???

f_start = -9.5e6 # Band left side
f_end = 9.5e6 # Band right side
k = (f_end - f_start) / chirp_duration # Band divided by singular chirp

# Complex exponential chirp scaled to 16-bit DAC range (2^14)
phase = 2 * np.pi * (f_start * t + 0.5 * k * t**2) # Confusing phase calculation for the chirp ???
iq = np.exp(1j * phase) * (2**14) # IQ data

# 4. Upload cyclic chirp buffer to Pluto FPGA DMA
sdr.tx(iq) # Start chirp transmission
print("Cyclic 20 MHz chirp running in FPGA.") # Print statement to verify that transmission has began.

# 5. Store 4 Fastlock Profiles covering 2402 - 2482 MHz
# Access raw libiio TX LO channel to write Fastlock sysfs attributes
phy = sdr.ctx.find_device("ad9361-phy")
tx_lo = phy.find_channel("altvoltage1", is_output=True) # Establish local oscillator as the signal source.

hop_freqs = [2412000000, 2432000000, 2452000000, 2472000000] # Attacked bands' center frequencies.

for profile_id, freq in enumerate(hop_freqs): # Cycle through the Attack bands' center frequencies.
  tx_lo.attrs["frequency"].value = str(freq) # Store values one-by-one to TX_LO attributes.
  time.sleep(0.05)  # Allow VCO calibration to settle once during setup
  tx_lo.attrs["fastlock_store"].value = str(profile_id) # Store the fastlock profiles.
  print(f"Stored Fastlock Profile {profile_id} at {freq / 1e6:.1f} MHz") # Displays saved fastlock channel's stored value from attack band center frequencies.

print("Setup complete. You can now run the C hopper onboard the PlutoSDR.")
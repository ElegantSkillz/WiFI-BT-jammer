Vali kõigepealt,kas burst või sweep jamming. 
bursti puhul on failideks burst_hopper.c ja setup_burst_chirp.py
CW jaoks fast_hopper.c ja setup_chirp.py

Nüüd on vaja cross compilida
Kui gcc on olemas saab faili plutosse otse kopeerida, vastasel juhul:
ARM cross-compiler.

Linux terminalis:
arm-linux-gnueabihf-gcc -O3 fast_hopper.c -o fast_hopper
scp fast_hopper root@192.168.2.1:/tmp/

Nüüd pythoni script käima
python3 setup_chirp.py

Nüüd ssh plutosse:
ssh root@192.168.2.1
/tmp/fast_hopper

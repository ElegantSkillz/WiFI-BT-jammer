#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

// Verify iio:device index on your Pluto firmware (usually device0 or device1)
#define FASTLOCK_PATH "/sys/bus/iio/devices/iio:device1/out_altvoltage1_TX_LO_fastlock_recall"
#define TX_GAIN_PATH  "/sys/bus/iio/devices/iio:device1/out_voltage0_hardwaregain"

// Active transmit gain vs. muted attenuation (in dB)
#define ACTIVE_GAIN "-20.00"
#define MUTED_GAIN  "-89.00"

int main() {
    int fd_lock = open(FASTLOCK_PATH, O_WRONLY);
    int fd_gain = open(TX_GAIN_PATH, O_WRONLY);

    if (fd_lock < 0 || fd_gain < 0) {
        perror("Failed to open IIO sysfs attributes (check iio:device index)");
        return 1;
    }

    const char *profiles[4] = {"0", "1", "2", "3"};
    srand(time(NULL));

    printf("Starting bursty pseudo-random 2.4 GHz interference generator...\n");

    int last_idx = -1;
    while (1) {
        // 1. ACTIVE BURST PHASE: Perform 2 to 5 rapid hops
        int hops_in_burst = 2 + (rand() % 4);
        write(fd_gain, ACTIVE_GAIN, strlen(ACTIVE_GAIN));

        for (int h = 0; h < hops_in_burst; h++) {
            int idx = rand() % 4;
            if (idx == last_idx) {
                idx = (idx + 1) % 4;
            }
            last_idx = idx;

            // Recall Fastlock profile (~20 us RF settle time)
            write(fd_lock, profiles[idx], 1);

            // Randomize dwell time between 200 us and 600 us (1 to 3 DMA frames)
            int dwell_us = 200 + (rand() % 401);
            usleep(dwell_us);
        }

        // 2. QUIET / BACKOFF PHASE: Mute TX so Wi-Fi/BLE devices initiate packets
        write(fd_gain, MUTED_GAIN, strlen(MUTED_GAIN));

        // Sleep 1 ms to 6 ms (mimics inter-frame spacing & congestion lulls)
        int quiet_us = 1000 + (rand() % 5001);
        usleep(quiet_us);
    }

    close(fd_lock);
    close(fd_gain);
    return 0;
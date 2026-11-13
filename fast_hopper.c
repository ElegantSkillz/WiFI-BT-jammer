#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>

// Sysfs path for AD9363 TX LO Fastlock recall on PlutoSDR
#define FASTLOCK_PATH "/sys/bus/iio/devices/iio:device1/out_altvoltage1_TX_LO_fastlock_recall"

int main() {
    int fd = open(FASTLOCK_PATH, O_WRONLY); // Open fastlock recall.
    if (fd < 0) { // If fastlock recall opening is unsuccessful:
        perror("Failed to open fastlock_recall (verify iio:device1 path)"); // return an error.
        return 1; // break out of the main loop.
    }

    const char *profiles[4] = {"0", "1", "2", "3"}; // Stored fastlock profiles
    srand(time(NULL));

    printf("Starting pseudo-random 2.4 GHz ISM hopping (Ctrl+C to stop)...\n"); // Start pseudo hopping

    int last_idx = -1; // Initialize last_idx at -1 so the first choice will no enter the if clause.
    while (1) {
        // Pick a pseudo-random profile different from the current one.
        int idx = rand() % 4; // Modulo division of a random integer returns always a value from 0-3.
        if (idx == last_idx) { // If the last value would be the new value, then:
            idx = (idx + 1) % 4; // Another roll is done to find another value.
        }
        last_idx = idx; // Update the last value as the previous one.

        // Trigger hardware Fastlock recall (~20 us RF settle time)
        write(fd, profiles[idx], 1); // Write a new value that was rolled to the fastlock channel select.

        // Dwell for 300 us (allows 12 full 25 us chirps across the 20 MHz slice)
        usleep(300); // Dwell to sweep the channel for several times.
    }

    close(fd); // Close write.
    return 0; // Reboot loop.
}
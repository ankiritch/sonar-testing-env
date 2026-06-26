import matplotlib.pyplot as plt
import numpy
import numpy as np
from typing import NamedTuple

# TYPES
class Position(NamedTuple):
    x: float
    y: float
    z: float

class Emitter(NamedTuple):
    position: Position

class Receiver(NamedTuple):
    position: Position
    inc_signal: numpy.ndarray

class ReflectiveSurface(NamedTuple):
    position: Position
    reflection_coefficient: float

# START VARIABLES
WAVE_SPEED = 343 # m/s, speed of sound in air
SIGNAL_FREQUENCY = 40000
SAMPLE_FREQUENCY = 500000
receivers: list[Receiver] = []
reflective_surfaces: list[ReflectiveSurface] = []

# FUNCTIONS
def generate_emitter_signal(
        signal_amplitude: float,
        signal_frequency: float,
        pulse_duration: float,
        duration: float,
        sample_frequency: float) -> numpy.ndarray:
    total_samples = int(duration * sample_frequency)
    pulse_samples = int(pulse_duration * sample_frequency)

    t_pulse = np.linspace(0, pulse_duration, pulse_samples, endpoint=False)
    pulse = signal_amplitude * np.sin(2 * np.pi * signal_frequency * t_pulse)

    full_signal = np.zeros(total_samples)
    full_signal[:pulse_samples] = pulse

    return full_signal

def get_distance(
        position1: Position,
        position2: Position) -> float:
    return np.sqrt( (position1.x-position2.x)**2 + (position1.y-position2.y)**2 + (position1.z-position2.z)**2)

def generate_received_signal(
        emitter: Emitter,
        receiver: Receiver,
        signal: numpy.ndarray,
        sample_frequency: float,
        reflective_surfaces: list[ReflectiveSurface]) -> numpy.ndarray:
    net_signal = np.zeros_like(signal)

    for reflective_surface in reflective_surfaces:
        distance_to_surface = get_distance(emitter.position, reflective_surface.position)
        distance_to_receiver = get_distance(reflective_surface.position, receiver.position)
        total_distance = distance_to_surface + distance_to_receiver

        signal_at_receiver = (signal * reflective_surface.reflection_coefficient)/ (distance_to_surface * distance_to_receiver)

        signal_delay = int((total_distance/WAVE_SPEED) * sample_frequency)

        if signal_delay < len(signal):
            delayed_signal = np.roll(signal_at_receiver, signal_delay)
            delayed_signal[:signal_delay] = 0.0
            net_signal += delayed_signal
        else:
            pass


    return net_signal


def listen(
        emitter: Emitter,
        receivers: list[Receiver],
        signal: numpy.ndarray,
        sample_frequency: float,
        signal_frequency: float,
        reflective_surfaces: list[ReflectiveSurface],
        listen_theta: float,
        listen_phi: float,
        listen_distance: float) -> float:
    inc_signals = []
    for i in range(len(receivers)):
        inc_signals.append(
            generate_received_signal(emitter, receivers[i], signal, sample_frequency, reflective_surfaces))


    mic_spacing = 0.004
    time_delay = (mic_spacing * np.sin(listen_theta)) / WAVE_SPEED
    sample_count_shift = int(round(time_delay * sample_frequency))

    aligned_signal_0 = np.roll(inc_signals[0], sample_count_shift)

    if sample_count_shift > 0:
        aligned_signal_0[:sample_count_shift] = 0.0
    elif sample_count_shift < 0:
        aligned_signal_0[sample_count_shift:] = 0.0

    beamformed_output = aligned_signal_0 + inc_signals[2]

    return beamformed_output




test_signal = generate_emitter_signal(signal_amplitude=1, signal_frequency=SIGNAL_FREQUENCY, pulse_duration=0.00005, duration=0.05, sample_frequency=SAMPLE_FREQUENCY)

central_emitter = Emitter(Position(0,0,0))

LU_receiver = Receiver(Position(-0.002, 0.002, 0), np.zeros(1))
LL_receiver = Receiver(Position(-0.002, -0.002, 0), np.zeros(1))
RU_receiver = Receiver(Position(0.002, 0.002, 0), np.zeros(1))
RL_receiver = Receiver(Position(0.002, -0.002, 0), np.zeros(1))

receivers.append(LU_receiver)
receivers.append(LL_receiver)
receivers.append(RU_receiver)
receivers.append(RL_receiver)


surface1 = ReflectiveSurface(Position(5, 0, 2), 1)
reflective_surfaces.append(surface1)

surface2 = ReflectiveSurface(Position(0, 0, 2), 1)
reflective_surfaces.append(surface2)

surface4 = ReflectiveSurface(Position(1, 0, 1), 1)
reflective_surfaces.append(surface4)

surface3 = ReflectiveSurface(Position(-1, 0, 2), 1)
reflective_surfaces.append(surface3)


# surface3 = ReflectiveSurface(Position(0, 0, 1), 1)
# reflective_surfaces.append(surface3)

LU_rcv_sig = generate_received_signal(central_emitter, LU_receiver, test_signal,SAMPLE_FREQUENCY, reflective_surfaces)
LL_rcv_sig = generate_received_signal(central_emitter, LL_receiver, test_signal,SAMPLE_FREQUENCY, reflective_surfaces)
RU_rcv_sig = generate_received_signal(central_emitter, RU_receiver, test_signal,SAMPLE_FREQUENCY, reflective_surfaces)
RL_rcv_sig = generate_received_signal(central_emitter, RL_receiver, test_signal,SAMPLE_FREQUENCY, reflective_surfaces)

listen_result = []

#for angle in range(-300, 300, ):
#    listen_result.append(listen(central_emitter, receivers, test_signal, SAMPLE_FREQUENCY, SIGNAL_FREQUENCY, reflective_surfaces, angle/100, 0, 0))

#fig, axes = plt.subplots(5, 1, figsize=(10, 8), sharex=True, sharey=True)

#
# axes[0].plot(LU_rcv_sig, color='crimson', lw=0.7)
# axes[0].set_title("Top-Left Receiver")
#
# axes[1].plot(RU_rcv_sig, color='darkorange', lw=0.7)
# axes[1].set_title("Top-Right Receiver")
#
# axes[2].plot(LL_rcv_sig, color='forestgreen', lw=0.7)
# axes[2].set_title("Bottom-Left Receiver")
#
# axes[3].plot(RL_rcv_sig, color='royalblue', lw=0.7)
# axes[3].set_title("Bottom-Right Receiver")
#
# axes[4].plot(listen_result, color='royalblue', lw=0.7)
# axes[4].set_title("Result")
#
# for ax in axes:
#     ax.set_ylabel("Amplitude")
#     ax.grid(True, alpha=0.3)
#
# axes[3].set_xlabel("Sample Index")
#
# plt.tight_layout()
# plt.show()

# angles_deg = np.linspace(-90, 90, 181)
# energy_profile = []
#
#
# for angle in angles_deg:
#     angle_rad = np.radians(angle)
#
#     result_signal = listen(
#         central_emitter, receivers, test_signal,
#         SAMPLE_FREQUENCY, SIGNAL_FREQUENCY, reflective_surfaces,
#         angle_rad, 0, 0
#     )
#
#     total_energy = np.sum((result_signal) ** 2)
#     energy_profile.append(total_energy)
#
#
# plt.figure(figsize=(8, 4))
# plt.plot(angles_deg, energy_profile, color='crimson', lw=2)
# plt.title("Sonar Spatial Beamforming Scan")
# plt.xlabel("Look Angle (Degrees)")
# plt.ylabel("Received Array Energy")
# plt.grid(True, alpha=0.4)
# plt.legend()
# plt.show()

angles_deg = np.linspace(-90, 90, 18)

WINDOW_SIZE = 125
num_bins = len(test_signal) // WINDOW_SIZE

hardware_radar_map = np.zeros((len(angles_deg), num_bins))

for a_idx, angle in enumerate(angles_deg):
    angle_rad = np.radians(angle)

    result_signal = listen(
        central_emitter, receivers, test_signal,
        SAMPLE_FREQUENCY, SIGNAL_FREQUENCY, reflective_surfaces,
        angle_rad, 0, 0
    )

    # Process data in sequential time steps (Simulating the Hardware Integration Bins)
    for b_idx in range(num_bins):
        start_sample = b_idx * WINDOW_SIZE
        end_sample = start_sample + WINDOW_SIZE

        chunk = result_signal[start_sample:end_sample]
        chunk_energy = np.sum(chunk ** 2)

        hardware_radar_map[a_idx, b_idx] = chunk_energy


plt.figure(figsize=(10, 5))
max_dist = (len(test_signal) / SAMPLE_FREQUENCY) * WAVE_SPEED / 2

plt.imshow(hardware_radar_map, aspect='auto', extent=[0, max_dist, 90, -90], cmap='magma')
plt.title("Tiny Tapeout Hardware Emulated Sonar Map")
plt.xlabel("Distance Range Bins (Meters)")
plt.ylabel("Look Angle (Degrees)")
plt.colorbar(label="Register Integration Value")
plt.show()
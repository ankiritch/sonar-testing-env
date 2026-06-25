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
        reflective_surfaces: list[ReflectiveSurface],
        listen_theta: float,
        listen_phi: float,
        listen_distance: float) -> numpy.ndarray:

    for i in range(len(receivers)):
        receivers[i].inc_signal = generate_received_signal(emitter, receivers[i], signal, sample_frequency, reflective_surfaces)


    return




test_signal = generate_emitter_signal(signal_amplitude=1, signal_frequency=40000, pulse_duration=0.002, duration=0.1, sample_frequency=SAMPLE_FREQUENCY)

central_emitter = Emitter(Position(0,0,0))

LU_receiver = Receiver(Position(-0.01, 0.01, 0), np.zeros(1))
LL_receiver = Receiver(Position(-0.01, -0.01, 0), np.zeros(1))
RU_receiver = Receiver(Position(0.01, 0.01, 0), np.zeros(1))
RL_receiver = Receiver(Position(0.01, -0.01, 0), np.zeros(1))

receivers.append(LU_receiver)
receivers.append(LL_receiver)
receivers.append(RU_receiver)
receivers.append(RL_receiver)


surface1 = ReflectiveSurface(Position(0, 5, 5), 1)
reflective_surfaces.append(surface1)

surface2 = ReflectiveSurface(Position(0, 0, 5), 1)
reflective_surfaces.append(surface2)

LU_rcv_sig = generate_received_signal(central_emitter, LU_receiver, test_signal,SAMPLE_FREQUENCY, reflective_surfaces)
LL_rcv_sig = generate_received_signal(central_emitter, LL_receiver, test_signal,SAMPLE_FREQUENCY, reflective_surfaces)
RU_rcv_sig = generate_received_signal(central_emitter, RU_receiver, test_signal,SAMPLE_FREQUENCY, reflective_surfaces)
RL_rcv_sig = generate_received_signal(central_emitter, RL_receiver, test_signal,SAMPLE_FREQUENCY, reflective_surfaces)


fig, axes = plt.subplots(4, 1, figsize=(10, 8), sharex=True, sharey=True)


axes[0].plot(LU_rcv_sig, color='crimson', lw=0.7)
axes[0].set_title("Top-Left Receiver")

axes[1].plot(RU_rcv_sig, color='darkorange', lw=0.7)
axes[1].set_title("Top-Right Receiver")

axes[2].plot(LL_rcv_sig, color='forestgreen', lw=0.7)
axes[2].set_title("Bottom-Left Receiver")

axes[3].plot(RL_rcv_sig, color='royalblue', lw=0.7)
axes[3].set_title("Bottom-Right Receiver")

for ax in axes:
    ax.set_ylabel("Amplitude")
    ax.grid(True, alpha=0.3)

axes[3].set_xlabel("Sample Index")

plt.tight_layout()
plt.show()
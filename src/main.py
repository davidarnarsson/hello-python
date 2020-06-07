import pyaudio
import time
import oscillators as osc
from intervaltree import IntervalTree, Interval

SAMPLE_RATE = 44100
BIT_DEPTH = 16
BYTES = int(BIT_DEPTH / 8)
CHANNELS = 1
MAX_AMPLITUDE = 2 ** 14
A = 440
NOTES = ["a", "a#", "b", "c", "c#", "d", "d#", "e", "f", "f#", "g", "g#"]


def hz(note, octave=4):
    val = 13.7 * 1.059463 ** (NOTES.index(note) + (octave + 1) * 12)
    print(f"{note}{octave} = {val}")

    return val


def lerp(v0, v1, t):
    return (1 - t) * v0 + t * v1


class Note:
    def __init__(self, pitch, start, length, velocity=1):
        self.pitch = pitch
        self.start = start
        self.length = length
        self.velocity = velocity


# this is a shit solution, but reading papers about temporal data structures
# is out of scope :)
class Sequencer:
    sortkey = lambda n: n.start + n.length

    def __init__(self):
        self.notes = IntervalTree()

    def add(self, note):
        self.notes.addi(note.start, note.start + note.length, note)

    def remove(self, note):
        self.notes.removei(note.start, note.start + note.length, note)

    def length(self):
        return self.notes.end()

    def sample_at(self, t):

        # again, bad
        current = self.notes.at(t)

        acc = 0
        for note in current:
            note_pos = t - note.begin
            acc += (
                osc.sine(note_pos, note.data.pitch)
                * note.data.velocity
                * adsr(note_pos, note.end - note.begin)
            ) * (1 / len(current))

        return acc


def adsr(i, n):
    pct = i / n

    if pct < 0.1:
        return lerp(0, 1, pct / 0.1)

    if pct > 0.65:
        return lerp(1, 0, (pct - 0.65) / 0.35)

    return 1


def to_byte(sample):
    return int(sample * MAX_AMPLITUDE).to_bytes(BYTES, byteorder="little", signed=True)


def main():
    seq = Sequencer()

    duration = 4

    notes = [
        Note(hz("a", octave=2), 0, duration),
        Note(hz("a", octave=3), 0, duration),
        Note(hz("a"), 0, duration),
        Note(hz("c#"), 0, duration),
        Note(hz("e"), 0, duration),
        Note(hz("a", octave=5), 0, duration),
        Note(hz("b", octave=5), 0, duration),
        Note(hz("c#", octave=5), 0, duration),
        Note(hz("e", octave=5), 0, duration),
        Note(hz("g#", octave=5), 0, duration),
        Note(hz("g#", octave=6), 0, duration),
        Note(hz("a", octave=6), 0, duration),
    ]

    [seq.add(note) for note in notes]

    p = pyaudio.PyAudio()

    stream = p.open(
        format=p.get_format_from_width(BYTES),
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        output=True,
    )

    start = time.perf_counter()
    samples = [
        seq.sample_at(i / (SAMPLE_RATE * CHANNELS))
        for i in range(int(seq.length() * SAMPLE_RATE * CHANNELS))
    ]
    end = time.perf_counter()

    print(f"Sampling took {end - start}s")

    # print(f"Sequencer length: {seq.length()} sample_at: {seq.sample_at(0.5)}")

    [stream.write(to_byte(sample)) for sample in samples]

    stream.stop_stream()
    stream.close()

    p.terminate()


if __name__ == "__main__":
    main()

# HackRF One: first receive-only demos

This is a small starter kit for a HackRF One.  It deliberately starts with
**receive-only** examples: checking the device, recording a short IQ capture,
plotting its spectrum, and listening to a local broadcast-FM station.  No
transmit programs are included.

> RF rules vary by country. Receive only signals you are permitted to receive;
> do not connect the HackRF's antenna port to a transmitter or powered RF
> source. Start with low gain, and use an appropriate antenna for the band.

## What you need

* A HackRF One, USB cable, and a suitable antenna.
* Linux packages: `hackrf` (provides `hackrf_info` and `hackrf_transfer`),
  Python 3, NumPy, and Matplotlib.

On Ubuntu/Debian:

```bash
sudo apt update
sudo apt install hackrf python3-numpy python3-matplotlib
```

Then confirm that the board is detected:

```bash
hackrf_info
```

It should show a serial number and `HACKRF_ONE`. If it says permission denied,
log out and in after adding your user to the `plugdev` group:

```bash
sudo usermod -aG plugdev "$USER"
```

If no device is found, try a data-capable USB cable and another USB port. Do
not run a firmware update merely to solve a cable/permission problem; compare
the firmware versions shown by `hackrf_info` with the official HackRF
documentation first.

## Install desktop SDR software (Ubuntu/Debian)

The following steps are for Ubuntu 24.04 / Debian-like systems. They favour
packages from the distribution or an application's official release—not random
PPAs. First install the HackRF driver and useful diagnostics once:

```bash
sudo apt update
sudo apt install hackrf soapysdr-tools soapysdr0.8-module-hackrf
hackrf_info
SoapySDRUtil --find
```

`hackrf_info` must find the board before trying a graphical program. The Soapy
command should list a HackRF device; it is primarily used by CubicSDR.

### GNU Radio Companion: build your own receiver

GNU Radio Companion (GRC) is the visual, block-diagram editor. It is the best
choice when you want to understand the DSP chain or adapt it to a project.

1. Install GNU Radio and the Osmocom source block used by HackRF:

   ```bash
   sudo apt install gnuradio gr-osmosdr
   volk_profile
   gnuradio-companion
   ```

   `volk_profile` is a one-time optional CPU optimization step and can take a
   few minutes. The window that opens is GRC.

2. In GRC, make a new flowgraph. Add these blocks by typing their names into
   the block search:

   ```text
   Osmocom Source → Rational Resampler → WBFM Receive → Audio Sink
   ```

3. Set the **Osmocom Source** properties:

   ```text
   Device arguments: hackrf=0
   Sample rate:      2400000
   Center frequency: 99500000       (replace with a local FM station)
   LNA gain:         16
   VGA gain:         20
   ```

4. Set **Rational Resampler** to `Interpolation = 1`, `Decimation = 10`, which
   changes the 2.4 MS/s source into 240 kS/s. Set **WBFM Receive** to `Quad
   Rate = 240000`, `Audio Decimation = 5`; this produces 48 kHz audio. Connect
   its output to **Audio Sink** and set that sink's sample rate to `48000`. Add
   a **QT GUI Frequency Sink** in parallel with the source if you want a live
   spectrum/waterfall.

5. Press Run (or F6). If there is no audio, confirm the device in
   `hackrf_info`, select the correct audio output in your desktop settings, and
   make sure the chosen frequency is a local broadcast-FM carrier.

Save the flowgraph as `fm_receiver.grc`. The included `fm_demod.py` is the
same basic idea in a compact offline program.

### SDR++: easiest modern waterfall receiver

SDR++ is a polished interactive receiver with waterfall, demodulator modes,
audio controls, and recording. On Ubuntu, use its **official Debian package**;
the project specifically advises against the distribution `sdrpp` package.

1. Download the `sdrpp_debian_amd64.deb` asset for the current stable release
   from the [official SDR++ releases](https://github.com/AlexandreRouma/SDRPlusPlus/releases).
2. In the directory containing that download, install it:

   ```bash
   sudo apt install ./sdrpp_debian_amd64.deb
   sdrpp
   ```

3. In SDR++, choose **Source → HackRF**, then set a sample rate such as
   `2.4 MHz`, tune to a local station, and press the play button. Select **WFM**
   for broadcast FM, set audio output, and begin with modest RF/IF gain.

### CubicSDR: simple cross-platform receiver

CubicSDR has a straightforward device picker, waterfall, and familiar AM/FM/
SSB controls. Install it from Ubuntu's repository:

```bash
sudo apt install cubicsdr
CubicSDR
```

At the first launch choose **HackRF** in the device window. Set `2.4 MS/s`,
tune a broadcast station, choose **FM**, and raise gain slowly. If the HackRF
is absent from the picker, run `SoapySDRUtil --find`; reinstall the
`soapysdr0.8-module-hackrf` package if it does not appear there.

### Gqrx: familiar receiver interface (optional)

Gqrx is another good desktop receiver for AM, FM, and SSB. It supports HackRF,
but on the Ubuntu release used by this machine it is not currently available
from the enabled APT repositories. Its upstream project provides releases and
source instructions at [Gqrx on GitHub](https://github.com/gqrx-sdr/gqrx).
Use SDR++ or CubicSDR first; they are the simpler supported installs here. If
you later install Gqrx, run `volk_profile` once, launch `gqrx`, select HackRF
in the initial device dialog, use a 2.4 MS/s rate, then choose WFM for an FM
broadcast station.

### Other Linux distributions

For GNU Radio use your normal package manager, then install your distribution's
HackRF driver package as well:

```bash
# Fedora
sudo dnf install gnuradio hackrf

# Arch Linux
sudo pacman -S gnuradio hackrf
```

The SDR++ official Linux package is Debian-specific; on other distributions use
its upstream build instructions. CubicSDR's AppImage release is a convenient
fallback: download it from the [official releases](https://github.com/cjcliffe/CubicSDR/releases),
make that exact downloaded file executable with `chmod +x`, then run it.

## The three demos

Run commands from this repository.

### 1. Inspect the receiver

```bash
./scripts/device_check.sh
```

This reports the connected device and tells you whether the two command-line
tools used by the examples are installed.

### 2. Capture and see radio spectrum

For example, record five seconds around 100 MHz (broadcast FM):

```bash
python3 scripts/capture_iq.py \
  --frequency 100e6 --sample-rate 10e6 --duration 5 \
  --lna-gain 16 --vga-gain 20 --output captures/fm-100MHz.cs8

python3 scripts/inspect_iq.py captures/fm-100MHz.cs8 \
  --frequency 100e6 --sample-rate 10e6 --output captures/fm-100MHz-spectrum.png
```

Open the resulting PNG. Peaks are signals; the broad spike exactly at the
middle is commonly receiver DC offset, not a station. Change `100e6` to a
locally licensed broadcast frequency. The capture is raw signed 8-bit,
interleaved I/Q (`.cs8`), so its expected size is roughly
`duration × sample_rate × 2` bytes.

### 3. Demodulate broadcast FM to a WAV file

Use a known local **broadcast** FM station. A 2.4 MHz sample rate keeps the
files modest and converts exactly to the WAV rate used by the demonstrator:

```bash
python3 scripts/capture_iq.py \
  --frequency 99.5e6 --sample-rate 2.4e6 --duration 20 \
  --lna-gain 16 --vga-gain 20 --output captures/station.cs8

python3 scripts/fm_demod.py captures/station.cs8 \
  --sample-rate 2e6 --output captures/station.wav
```

Play it with `aplay captures/station.wav`, VLC, or your usual media player.
Tune `--frequency` to the station's carrier. If the audio is weak or noisy,
move the antenna, then adjust gains gradually; a clipped, overloaded capture
cannot be repaired afterwards.

## Tool map

| Tool | Best use |
| --- | --- |
| `hackrf_info` | Device/firmware/USB sanity check |
| `hackrf_transfer` | Record or replay raw IQ; these examples use only recording (`-r`) |
| `scripts/capture_iq.py` | Safe wrapper around a timed `hackrf_transfer` capture |
| `scripts/inspect_iq.py` | Turn a capture into an annotated spectrum PNG |
| `scripts/fm_demod.py` | Educational mono wideband-FM demodulator to WAV |
| [SDR++](https://www.sdrpp.org/) or [GNU Radio](https://wiki.gnuradio.org/) | Interactive exploration and larger DSP projects |

## Practical operating notes

* Begin with the supplied antenna and a strong broadcast signal. Antenna
  choice matters more than aggressive gain.
* The HackRF is half-duplex: it cannot transmit and receive at the same time.
* `--lna-gain` accepts 0–40 dB in 8 dB steps; `--vga-gain` accepts 0–62 dB in
  2 dB steps. Start around 16/20. Lower either gain if much of the spectrum
  rises or stations smear together; raise gradually if it is quiet.
* A sample rate sets the width captured, not the RF frequency. 10 MHz captures
  approximately a 10 MHz-wide view around the chosen centre; 2 MHz is a good
  starting point for one FM station.
* Capture files grow quickly: 10 MS/s uses about 20 MB/s. They are ignored by
  Git in this repository.

## Useful next steps

* Use the spectrum script to find a clear local FM peak, then retune the
  capture exactly onto it.
* Explore SDR++ for a waterfall, filters, and supported broadcast demodulators.
* GNU Radio's `Osmocom Source` lets you build the same receive chain visually:
  source → frequency translating filter → WBFM receive → audio sink.

Keep raw IQ captures and the frequency/sample-rate/gain settings together.
Those settings are required to interpret a capture correctly.

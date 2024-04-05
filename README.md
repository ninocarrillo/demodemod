# pymodem
Simple packet radio demodulators (and some day maybe modulators) written in Python. Intended to help people better understand some signal processing methods used in dsp-based packet radio.

Currently working:
- AFSK demodulator
- AX.25 decoder
- IL2P+CRC decoder

IL2P+CRC decoder is working but I have not fully tested and validated it for all header types and packet lengths yet. If you do, please give feedback!

I plan to add PSK, and transmit waveform generators.

Several sample audio files are included in AX.25, IL2P and IL2P+CRC format. The sample files have additive white gaussian noise at progressively increasing amplitude.

afsk_decode.py can be used to decode any wav file containing AFSK samples. The sample rate will be automatically detected from the wav file. You'll need to set up the symbol rate and mark/tone frequencies for the desired mode within the script. It's currently set for 300 bps 1600/1800 IL2P+CRC.

## Requirements:
- Python3
- NumPy
- SciPy

## Usage
```
python3 afsk_decode.py afsk_300_il2pc_noise.wav
```

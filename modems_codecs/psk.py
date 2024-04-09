# afsk
# Python3
# Functions for demodulating PSK
# Nino Carrillo
# 9 Apr 2024

from scipy.signal import firwin
from math import ceil
from numpy import arange, sin, cos, pi, convolve, sqrt

class BPSKModem:

	def __init__(self, **kwargs):
		self.definition = kwargs.get('config', '300')
		self.sample_rate = kwargs.get('sample_rate', 8000)

		if self.definition == '300':
			# set some default values for 300 bps AFSK:
			self.agc_attack_rate = 5.0		# Normalized to 1.0 / sec
			self.agc_sustain_time = 0.001	# sec
			self.agc_decay_rate = 500.0			# Normalized to 1.0 / sec
			self.symbol_rate = 300.0			# symbols per second (or baud)
			self.input_bpf_low_cutoff = 1100.0	# low cutoff frequency for input filter
			self.input_bpf_high_cutoff = 1900.0	# high cutoff frequency for input filter
			self.input_bpf_span = 4.80			# Number of symbols to span with the input
											# filter. This is used with the sampling
											# rate to determine the tap count.
											# more taps = shaper cutoff, more processing
			self.carrier_freq = 1500.0				# carrier tone frequency
			self.output_lpf_cutoff = 200.0		# low pass filter cutoff frequency for
											# output signal after I/Q demodulation
			self.output_lpf_span = 1.5			# Number of symbols to span with the output


		self.tune()

	def retune(self, **kwargs):
		self.symbol_rate = kwargs.get('symbol_rate', self.symbol_rate)
		self.input_bpf_low_cutoff = kwargs.get('input_bpf_low_cutoff', self.input_bpf_low_cutoff)
		self.input_bpf_high_cutoff = kwargs.get('input_bpf_high_cutoff', self.input_bpf_high_cutoff)
		self.input_bpf_span = kwargs.get('input_bpf_span', self.input_bpf_span)
		self.mark_freq = kwargs.get('mark_freq', self.mark_freq)
		self.output_lpf_cutoff = kwargs.get('output_lpf_cutoff', self.output_lpf_cutoff)
		self.output_lpf_span = kwargs.get('output_lpf_span', self.output_lpf_span)
		self.sample_rate = kwargs.get('sample_rate', self.sample_rate)

		self.tune()

	def tune(self):
		self.input_bpf_tap_count = round(
			self.sample_rate * self.input_bpf_span / self.symbol_rate
		)
		self.output_lpf_tap_count = round(
			self.sample_rate * self.output_lpf_span / self.symbol_rate
		)

		# Use scipy.signal.firwin to generate taps for input bandpass filter.
		# Input bpf is implemented as a Finite Impulse Response filter (FIR).
		self.input_bpf = firwin(
			self.input_bpf_tap_count,
			[ self.input_bpf_low_cutoff, self.input_bpf_high_cutoff ],
			pass_zero='bandpass',
			fs=self.sample_rate
		)

		# Use scipy.signal.firwin to generate taps for output low pass filter.
		# Output lpf is implemented as a Finite Impulse Response filter (FIR).
		# firwin defaults to hamming window if not specified.
		self.output_lpf = firwin(
			self.output_lpf_tap_count,
			self.output_lpf_cutoff,
			fs=self.sample_rate
		)

		self.envelope = 0
		# adjust the agc attack and decay rates to per-sample values
		self.scaled_agc_attack_rate = self.agc_attack_rate / self.sample_rate
		self.scaled_agc_decay_rate = self.agc_decay_rate / self.sample_rate
		self.sustain_increment = self.agc_sustain_time / self.sample_rate
		print(self.sustain_increment)
		print(self.scaled_agc_attack_rate)
		print(self.scaled_agc_decay_rate)


	def demod(self, input_audio):
		# Apply the input filter.
		audio = convolve(input_audio, self.input_bpf, 'valid')

		self.do_agc(audio)

		for sample in audio:
			# do the costas loop
			pass

		# Apply the output filter:
		audio = convolve(audio, self.output_lpf, 'valid')
		return audio

	def peak_detect(self, sample):
		compare_value = abs(sample)
		if compare_value > self.envelope:
			self.envelope += (self.scaled_agc_attack_rate * self.agc_normal)
			if self.envelope > compare_value:
				self.envelope = compare_value
			self.sustain_count = 0
		if self.sustain_count >= self.agc_sustain_time:
			self.envelope -= (self.scaled_agc_decay_rate * self.agc_normal)
			if self.envelope < 0:
				self.envelope = 0
		self.sustain_count += self.sustain_increment

	def do_agc(self, buffer):
		# This routine applies a scaling factor to each sample in buffer.
		# The scaling factor is determined by the detected envelope.

		# For the agc attack and decay rates to makes sense, we need to have
		# some pre-knowledge about the maximum possible value of the data stream.
		self.agc_normal = 32768.0
		print(max(buffer))

		i = 0
		for sample in buffer:
			# detect the Envelope
			self.peak_detect(sample)
			# scale the sample
			# This will drive the signal stream to an amplitude of 0.5
			buffer[i] =  sample / (self.envelope)
			i += 1
		pass
# Wersi MK1/EX20 synthesizer

Enter the world of the Wersi™ MK1 synthesizers, one of the lesser known series of digital synthesizers by West-German organ and synthesizer manufacturer Wersi™. The MK1 "Stage performer", and its rack-mount sibling EX-20, were manufactured from around 1985 to 1988, as professional electronic synthesizers for stage and studio performance.

The MK1 series eventually faded into obscurity due to various design flaws and issues with the synthesizer itself, such as the notoriously difficult programming interface, uninspired factory presets, absence of editing tools and a lack of focus, further worsened by a halt in development due to a series of manufacturer bankruptcies.

Major efforts in reverse engineering and tracking down original documentation have resulted in the development of this editor, with the sole purpose being to overcome its design flaws and expose as much of the potential sound synthesis capabilities as possible in a modern and convenient way. To revive the purpose of this remarkable and digitally pioneering vintage synthesizer.

The fact that you are on this page likely means that you are one of the few owners of an original Wersi™ MK1 or EX-20 synthesizer. Congratulations! Sit tight, as you will now finally be able to properly use this synthesizer to your heart's content.

### Digital sound synthesis

At first sight, the interface of the MK1 suggests that it is a simple additive synthesizer capable of adding 32 sine harmonics, similar to the registers of an electric organ. However looks can deceive, as the MK1 actually contains an elaborate implementation of digital wavetable synthesis. Wavetables are used as basis for sound generation, consist of 64 of 32 samples each and are interpolated and resampled to any note frequency after which they are modulated with complex amplitude and frequency envelopes. Fourier transforms are only used to translate between the harmonic sliders in the interface and the actual sound synthesis modules.

Envelopes for amplitude and frequency modulation can be programmed through a set of predefined envelope modules, each of which can be chained after one another to provide changing ever-changing modulation as time progresses. All envelope calculations are performed by a Motorola 68B09 CPU and are converted to analog using a NatSemi 1232 DAC (12-bit).

Voice sound synthesis is fully digital (e.g. without VCO or DCO), performed by a Zilog Z8601 CPU + NatSemi 0832 DAC (8-bit), two of which are located on a single SL-M2 slave sound module. The MK1 synthesizer can be fitted with as much as 10 SL-M2 modules, enabling 20 individual polyphonic voices through a total of 20 CPUs.

### Analog characteristics

Each SL-M2 sound module contains an optional analog low-pass filter ("Bright"). Subsequently, all 20 sound module voices are combined and fed through a single AF-20 analog filter module, containing a digitally controlled mono SSM2044 VCF, mono distortion stage, mono noise stage, stereo phase effect stage ("WersiVoice") and finally a noise-reduction stage ("Dynafex").

Additionally, an optional DH-10 or DH-11 filter module mixes reverb, delay and compression into the final audio output.


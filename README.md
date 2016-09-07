# MEI Translator: from CMN-MEI to Mensural-MEI

The script takes a CMN (Common Music Notation) MEI file and translates it into a Mensural MEI file. It was developed for mensural pieces that are transcribed in Sibelius (following certain rules) and exported to MEI files with the SibMei plugin. These MEI files retrieved from Sibelius are actually CMN MEI files. The Common Music Notation (CMN) MEI module is appropriate to encode contemporary notation; but the pieces are actually in mensural notation, thus the Mensural MEI module is more appropriate to encode them. This is where the MEI Translator script comes into play, translating the CMN MEI file obtained from Sibelius to a Mensural MEI file.

The mensural pieces transcribed in Sibelius, from which the CMN MEI file is obtained, follow a set of rules developed by Dr. Karen Desmond. Examples of these rules are: using 'staccato marks' to show the 'dots' present in the manuscript (both of division or perfection), 'tenuto marks' to show downward stems in the manuscript that represent longer semibreves in ars antiqua, 'tremolo marks' for plicas, etc.

## Implementation
This project consist on three modules: arsantiqua, arsnova and MEI_Translator. The first two modules contain functions that deal with features characteristic from one of the two Medieval musical styles: Ars Antiqua and Ars Nova. For example: arsnova module deals with "partial imperfections" and also take into account "minims" and "prolatio"; arsantiqua, on the contrary, doesn't take any of these features into account, but instead it considers the presence of "major semibreves" and "duplex longas".

The MEI_Translator module contains the general functions for the translation, i.e., the functions that are common to both styles (antiqua and nova). This module can be used as a script for the user to run, along with certain paramenters (the piece name, the music style and the mensuration values for each voice), in order to start the translation process.

## Requirements 
Install the LibMEI library, found in: https://github.com/DDMAL/libmei
Look at the wiki for instructions on both the installation of the LibMEI C++ library, and the installation of the python bindings.

## Running the script
The parameters to run the script depend on the musical style of the piece intended to be translated into Mensural MEI. The two parameters that are common for both styles are: 
- the piece name (or its path, in case the piece is in a different directory from the script)
- the musical style, with only two values: "antiqua" and "nova"
 
The other parameters indicate the mensuration for each of the voices in the piece. There are two flags to enter the mensuration information for each voice: -NewVoiceN and -NewVoiceA. The -NewVoiceN flag is use exclusively for Ars Nova pieces (musical style = "nova"); while the -NewVoiceA flag is use only for Ars Antiqua pieces (musical style = "antiqua").

**New voice flag in Ars Nova: '-NewVoiceN'**

Use this flag for each new voice (in Ars Nova) that you are entering. After the flag, use the characters 'p' or 'i' to indicate the mensuration of one voice in the order: modusmajor, modusminor, tempus and prolatio.

**Example:**  

_`-NewVoiceN i p i p`_ 

Indicates a voice with imperfect modusmajor and tempus, and perfect modusminor and prolatio.

**New voice flag in Ars Antiqua: '-NewVoiceA'**

Use this flag for each new voice (in Ars Antiqua) that you are entering. After the flag, use the characters '2' or '3' to indicate the 'division of the breve', which can be duple or triple, and then use the characters 'p' or 'i' to indicte the 'modusminor'.

**Example:**  

_`-NewVoiceA 3 i`_ 

Indicates a voice with 3 minor semibreves per breve (triple division) and imperfect modusminor.

The order in which you enter the mensuration of the voices using the new voice flags (-NewVoiceN or -NewVoiceA) should be the same as the order of the voices in the CMN MEI file (or the Sibelius file).

**Examples:**

1. _`-NewVoiceN i i p p -NewVoice i p i p -NewVoiceN p i i i`_

Ars Nova 3-voice piece with different mensurations for each voice.

2. _`-NewVoiceA 2 p -NewVoiceA 2 p -NewVoiceA 2 p -NewVoiceA 2 p`_

Ars Antiqua 4-voice piece with the same mensuration for all its voices (duple divison of the breve and perfect modusminor).

### Examples:

Here there are two pieces, one for ars nova and one for ars antiqua, on which the translator can be run through. This pieces are included in this repository, on the TestFiles directory, so at the moment of downloading the whole repository you will be able to actually run any of the following examples.

Ars Nova piece: Zodiacum from the IvTrem

`$ python MEI_Translator.py TestFiles/IvTrem/zodiacum.mei nova -NewVoiceN i p i p -NewVoiceN i p i p -NewVoiceN i p i p`

Ars Antiqua piece: Sicut from the Fauvel

`$ python MEI_Translator.py TestFiles/Fauv/sicut.mei antiqua -NewVoiceA 3 p -NewVoiceA 3 p -NewVoiceA 3 p`

You can also go to the TestFiles directory and run:
`$ python processing.py`

This script will run all the instructions contained in the IvTremPieces.txt and/or FauvPieces.txt files, which will run the MEI_Translator over all the pieces in the IvTrem and/or Fauv directories, respectively.

## Using the module
The MEI_Translator can be run as a script, but it is a module, and you can take advantage of this functionality.

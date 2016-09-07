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

New voice flag in Ars Nova: '-NewVoiceN'
Use this flag for each new voice (in Ars Nova) that you are entering. After the flag, use the characters 'p' or 'i' to indicate the mensuration of one voice in the order: modusmajor, modusminor, tempus and prolatio.

Example:

_`-NewVoiceN i p i p`_ 
Indicates a voice with imperfect modusmajor and tempus, and perfect modusminor and prolatio.



For Ars Nova, the instruction is:

`$ python MEI_Translator.py <piece> nova -NewVoiceN modusmaior modusminor tempus prolatio -NewVoiceN modusmaior modusminor tempus prolatio`

For Ars Antiqua, the instruction is:

$ python MEI_Translator.py \<piece\> antiqua -NewVoiceA breve_division

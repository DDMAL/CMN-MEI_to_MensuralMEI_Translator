# MEI_Translator: from CMN-MEI to Mensural-MEI

The script takes a CMN (Common Music Notation) MEI file and translates it into a Mensural MEI file. It was developed for mensural pieces that are transcribed in Sibelius (following certain rules) and exported to MEI files with the [sibmei](https://github.com/music-encoding/sibmei) plugin. These MEI files retrieved from Sibelius are actually CMN MEI files. The Common Music Notation (CMN) MEI module is appropriate to encode contemporary notation; but the pieces are actually in mensural notation, thus the Mensural MEI module is more appropriate to encode them. This is where the MEI Translator script comes into play, translating the CMN MEI file obtained from Sibelius to a Mensural MEI file.

The Sibelius transcription of the pieces follows a set of rules developed by Dr. Karen Desmond. Examples of these rules are: using 'staccato marks' to show the 'dots' present in the manuscript (both of division or perfection), 'tenuto marks' to show downward stems in the manuscript that represent longer semibreves in ars antiqua, 'tremolo marks' for plicas, etc.

## Implementation
This project consist on three modules: arsantiqua, arsnova and MEI_Translator. The first two modules contain functions that deal with features characteristic from one of the two Medieval musical styles: Ars Antiqua and Ars Nova. For example: arsnova module deals with "partial imperfections" and also take into account "minims" and "prolatio"; arsantiqua, on the contrary, doesn't take any of these features into account, but instead it considers the presence of "major semibreves" and "duplex longas".

The MEI_Translator module contains the general functions for the translation, i.e., the functions that are common to both styles (antiqua and nova). This module can be used as a script for the user to run, along with certain paramenters (the piece name, the music style and the mensuration values for each voice), in order to start the translation process.

## Requirements 
Install the LibMEI library, found in: https://github.com/DDMAL/libmei. Look at the wiki for instructions on both the installation of the LibMEI C++ library, and the installation of the python bindings.

## Running the script
The parameters to run the script depend on the musical style of the piece intended to be translated into Mensural MEI. The two parameters that are common for both styles are: 
- the piece name (or its path, in case the piece is in a different directory from the script)
- the musical style, with only two values: "antiqua" and "nova"
 
The other parameters indicate the mensuration for each of the voices in the piece. There are two flags to enter the mensuration information for each voice: -NewVoiceN and -NewVoiceA. The -NewVoiceN flag is use exclusively for Ars Nova pieces (musical style = "nova"); while the -NewVoiceA flag is use only for Ars Antiqua pieces (musical style = "antiqua").

**New voice flag in Ars Nova: '-NewVoiceN'**

Use this flag for each new voice (in Ars Nova) that you are entering. After the flag, use the characters 'p' or 'i' to indicate the mensuration of one voice in the order: modusmajor, modusminor, tempus and prolatio.

**Example:**  _`-NewVoiceN i p i p`_ 

 Indicates a voice with imperfect modusmajor and tempus, and perfect modusminor and prolatio.

**New voice flag in Ars Antiqua: '-NewVoiceA'**

Use this flag for each new voice (in Ars Antiqua) that you are entering. After the flag, use the characters '2' or '3' to indicate the 'division of the breve', which can be duple or triple, and then use the characters 'p' or 'i' to indicte the 'modusminor'.

**Example:**  _`-NewVoiceA 3 i`_ 

 Indicates a voice with 3 minor semibreves per breve (triple division) and imperfect modusminor.

The order in which you enter the mensuration of the voices using the new voice flags (-NewVoiceN or -NewVoiceA) should be the same as the order of the voices in the CMN MEI file (or the Sibelius file).

**Examples with more than one voice:**

- _`-NewVoiceN i i p p -NewVoice i p i p -NewVoiceN p i i i`_

 Ars Nova 3-voice piece with different mensurations for each voice.

- _`-NewVoiceA 2 p -NewVoiceA 2 p -NewVoiceA 2 p -NewVoiceA 2 p`_

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
As we saw in the previous section, the MEI\_Translator can be run as a script. But the MEI\_Translator is a module, and it also can be used in this way.

Here are the steps to follow in order to use the MEI\_Translator as a module, to illustrate each step we are using as input file for the MEI Translator the piece _bona.mei_ from the IvTrem. To obtain the Mensural MEI file for this piece directly, you could also run the MEI\_Translator as a script with the following instruction: `python MEI_Translator.py TestFiles/IvTrem/bona.mei nova -NewVoiceN i p i p -NewVoiceN i p i p -NewVoiceN i i i p`.

1) On your python shell, import the pymei module and convert your piece into an pymei.MeiDocument object

`import pymei`

`cmn\_meidoc = pymei.documentFromFile("TestFiles/IvTrem/bona.mei").getMeiDocument()`

2) Import the MEI_Translator module and create a MensuralTranslation object, which will inherit all the methods from the pymei.MeiDocument class

`from MEI_Translator import MensuralTranslation`

`mensural\_meidoc = MensuralTranslation(cmn\_meidoc, "nova", [["i", "p", "i", "p"], ["i", "p", "i", "p"], ["i", "i", "i", "p"]])`

Now you will be able to use all the pymei.MeiDocument methods (_getElementsByName_, _getElementById_, etc.) and a new method included in the MensuralTranslation class (_getModifiedNotes_) to be able to access elements in the file and edit them before you call the function _documentToFile_ to create the file containing the Mensural MEI document.

### MeiDocument inherited methods:

We can use the inherited methods from pymei.MeiDocument to check that certain _MEI elements_ were actually removed in the translation process, like 'tie' and 'mRest' elements. Mensural notation doesn't use ties and, as it doesn't have measures, the Mensural-MEI module doesn't recognize 'mRest' elements (measure rests). So we can check if the 'tie' elements present in the CMN MEI document are still present in the Mensural MEI document by doing:

`cmn_meidoc.getElementsByName('tie')`

`mensural\_meidoc.getElementsByName('tie')`

As you notice, the second instruction returns a blank list. Same thing will happen with the 'mRest' elements. Actually, the script converts all 'mRest' elements into simple 'rest' elements. You can actually verify if this was done by writing the following instruction (it should return _True_):

`len(cmn\_meidoc.getElementsByName('rest')) + len(cmn\_meidoc.getElementsByName('mRest')) == len(mensural_meidoc.getElementsByName('rest'))`

### Additional methods:

The additional method _getModifiedNotes()_ returns a list of notes that have been modified from its default value (the value given by the mensuration); i.e., it returns a list of notes that have experienced _"imperfection"_, _"alteration"_, _"perfection"_, _"partial imperfection"_ or _"major semibreve"_. You can give any of these 5 string-values as a parameter to the method in order to return just the list of notes that experimented that specific modificaton type, or no-parameter at all in order to get the full list of notes modified by any of those five types.

Since _"major semibreve"_ is a modification available only in Ars Antiqua, you could run the following instructions to see the method working:

`import pymei`

`cmn_meidoc = pymei.documentFromFile("TestFiles/Fauv/fauvel_nous.mei").getMeiDocument()`

`from MEI_Translator import MensuralTranslation`

`mensural_meidoc = MensuralTranslation(cmn_meidoc, "antiqua", [["3", "p"], ["3", "p"], ["3", "p"]])`

`mensural_meidoc.getModifiedNotes('major semibreve')`

Also, _"partial imperfection"_ is a modification available only in Ars Nova pieces, if you want to see an example of it run the following code in your python shell, you will find some interesting results.

`import pymei`

`cmn_meidoc = pymei.documentFromFile("TestFiles/IvTrem/zodiacum.mei").getMeiDocument()`

`from MEI_Translator import MensuralTranslation`

`mensural_meidoc = MensuralTranslation(cmn_meidoc, "nova", [["i", "p", "i", "p"], ["i", "p", "i", "p"], ["i", "p", "i", "p"]])`

`mensural_meidoc.getModifiedNotes('partial imperfection')`

### Getting the Mensural MEI File: the _documentToFile_ function

You have already instantiated a MensuralTranslated object, that behaves just like a regular MeiDocument. You have played around with this document, getting its elements, you could also edit these elements. But you haven't actually generated any file, in order to do so you should use the __documentToFile__ function from the __pymei__ module (which you have already imported at the beginning of this section). Then, to get your Mensural MEI file from your MensuralTranslated object `mensural_meidoc`, you do:

`pymei.documentToFile(mensural_meidoc)`

With this instruction you will have the same output as if you have ran the MEI\_Translator as a script, the only difference is that you are still able to modify the Mensural MEI document (the MensuralTranslated object) as you wish and convert it to a file -_pymei.documentToFile()_- again.

# MEI_Translator: from CMN-MEI to Mensural-MEI

The MEI_Translator script takes a CMN (Common Music Notation) [MEI](http://music-encoding.org) file and translates it into a Mensural MEI file.<sup>[1](#one)</sup> It was developed for mensural music that was transcribed in Sibelius, and exported to MEI files with the [sibmei](https://github.com/music-encoding/sibmei) plugin. MEI files generated with Sibelius are CMN-MEI files. The CMN-MEI module encodes music from contemporary notation. Compositions written in mensural notation should use the Mensural MEI module. The MEI Translator encodes CMN-MEI files created with Sibelius to Mensural MEI files.

The Sibelius transcription of the pieces follows a set of rules developed by [Karen Desmond](https://www.brandeis.edu/facultyguide/person.html?emplid=5549ea5590219e2fd526777523c96d99ba7d1908). Examples of the rules are: 
- _staccato marks_ to show the _dots_ present in the manuscript (both of division or perfection)
- _tenuto marks_ to show downward stems in the manuscript that represent longer semibreves in ars antiqua
- _tremolo marks_ for plicas, etc.

## Implementation
The project consist on three modules: (1) arsantiqua, (2) arsnova, and (3) MEI_Translator. The first two modules contain functions that deal with features characteristic from one of the two Medieval musical styles: _Ars antiqua_ and _Ars nova_. The _arsnova_ module deals with "partial imperfections," and considers "minims" and "prolatio", while the _arsantiqua_ module considers the presence of "major semibreves" and "duplex longas."

The MEI_Translator module contains general functions for the translation, shared by both _Ars antiqua_ and _Ars nova_ styles. The user can run the module as a script, along with _piece name_, _music style_, and _mensuration value_ parameters.

## Requirements 
- The [LibMEI library](https://github.com/DDMAL/libmei). The wiki contains instructions on both the installation of the LibMEI C++ library, and the installation of the python bindings.

## Running the script
Parameters are set according to a composition's musical style. The two parameters that are common for both styles are: 
- the _piece name_, or the path to the piece if the composition is in a different directory than the script
- the _musical style_, two values: "antiqua" and "nova"
 
Other parameters indicate the mensuration for each of the voices in a composition. USe the following two flags to enter the mensuration definition for each voice: ```-NewVoiceN``` and ```-NewVoiceA```. The ```-NewVoiceN``` flag is used exclusively for _Ars nova_ pieces (musical style = "nova"), while the ```-NewVoiceA``` flag is use only for _Ars antiqua_ pieces (musical style = "antiqua").

#### New voice flag in _Ars nova_: ```-NewVoiceN```

Use this flag for each new voice (_Ars nova_) that you are entering. After the flag, use the characters ```p``` or ```i``` to indicate the mensuration of one voice in the order: _modus major_, _modus minor_, _tempus_ and _prolatio_.

##### Example:

> ``` -NewVoiceN i p i p``` indicates a voice with _imperfect modus major_ and _tempus_, and _perfect modus minor_ and _prolatio_.

#### New voice flag in Ars Antiqua: ```-NewVoiceA```

Use this flag for each new voice (_Ars antiqua_) that you are entering. After the flag, use the characters ```2``` or ```3``` to indicate the _division of the breve_, which can be _duple_ or _triple_, and then use the characters ```p``` or ```i``` to indicte the _modus minor_.

##### Example: 

> ```-NewVoiceA 3 i``` indicates a voice with 3 minor semibreves per breve (triple division) and _imperfect modus minor_.

The order in which you enter the mensuration of the voices using the new voice flags (```-NewVoiceN``` or ```-NewVoiceA```) should be the same as the order of the voices in the CMN MEI file (or the Sibelius file).

##### Examples with more than one voice:

> ```-NewVoiceN i i p p -NewVoice i p i p -NewVoiceN p i i i``` is used for an _Ars nova_ 3-voice piece with different mensurations for each voice.

> ```-NewVoiceA 2 p -NewVoiceA 2 p -NewVoiceA 2 p -NewVoiceA 2 p``` is used for and _Ars antiqua_ 4-voice piece with the same mensuration for all its voices (duple divison of the breve and _perfect modus minor_).

### Examples of running scripts from the command line

Here are two pieces, one for _Ars nova_ and one for _Ars antiqua_. The composition are included in this repository (_TestFiles_ directory).

_Ars nova_ piece: _Zodiacum_ from the IvTrem
> ```$ python MEI_Translator.py TestFiles/IvTrem/zodiacum.mei nova -NewVoiceN i p i p -NewVoiceN i p i p -NewVoiceN i p i p```

_Ars antiqua_ piece: _Sicut_ from the Fauvel
> ```$ python MEI_Translator.py TestFiles/Fauv/sicut.mei antiqua -NewVoiceA 3 p -NewVoiceA 3 p -NewVoiceA 3 p```

You can also go to the ```TestFiles``` directory and run:
> ```$ python processing.py```

The script above script runs all the instructions contained in the ```IvTremPieces.txt``` and/or ```FauvPieces.txt``` files, and runs the MEI\_Translator over all the pieces in the ```IvTrem``` and/or ```Fauv``` directories, respectively.

## Using the module
As we saw in the previous section how to run the MEI\_Translator as a script. But the MEI\_Translator can also be used as a module.

Here are the steps to follow in order to use the MEI\_Translator as a module. To illustrate each step we are using ```bona.mei``` from the ```IvTrem``` as an input file.<sup>[2](#two)<sup>

1) On your python shell, import the ```pymei``` module and convert your piece into a ```pymei.MeiDocument``` object:

```
import pymei

cmn_meidoc = pymei.documentFromFile("TestFiles/IvTrem/bona.mei").getMeiDocument()
```

2) Import the ```MEI_Translator``` module and create a ```MensuralTranslation``` object, which will inherit all the methods from the ```pymei.MeiDocument``` class:

```
from MEI_Translator import MensuralTranslation`

mensural_meidoc = MensuralTranslation(cmn_meidoc, "nova", [["i", "p", "i", "p"], ["i", "p", "i", "p"], ["i", "i", "i", "p"]])
```

Now you will be able to use all the ```pymei.MeiDocument``` methods (```getElementsByName```, ```getElementById```, etc.) and the ```MensuralTranslation``` class (```getModifiedNotes```) to be able to access elements in the file and edit them before you call the function ```documentToFile``` to create the file containing the Mensural MEI document.

### ```MeiDocument``` inherited methods:

We can use the inherited methods from ```pymei.MeiDocument``` to check that _MEI elements_ were actually removed in the translation process, like the ```tie``` and ```mRest``` elements. Since mensural notation does not use ties nor have measures, the Mensural-MEI module doesn't recognize ```mRest``` elements (measure rests). We can check if the ```tie``` elements present in the CMN-MEI document are still present in the Mensural MEI document by using:

```
cmn_meidoc.getElementsByName('tie')
mensural_meidoc.getElementsByName('tie')
```

The second method returns a blank list with either the ```tie``` and ```mRest``` elements provided as argumetns. The script converts all ```mRest``` elements into simple ```rest``` elements. You can actually verify the outcome by using the following code (which should return ```True```):

```
len(cmn_meidoc.getElementsByName('rest')) + len(cmn_meidoc.getElementsByName('mRest')) == len(mensural_meidoc.getElementsByName('rest'))
```

### Additional methods:

The ```getModifiedNotes()``` method returns a list of notes that have been modified from its default value (the value given by the mensuration), and returns a list of notes along with its mensural parameters: _"imperfection"_, _"alteration"_, _"perfection"_, _"partial imperfection"_ or _"major semibreve"_. You can pass any 5 string-values as a parameters to the method in order to return a list of notes with its mensural modificaton type, or you can omit the parameters to get a list of notes modified by any of those five modification types.

Since _"major semibreve"_ is a modification that occurs only in _Ars antiqua_, you could run the following code to see whether the method works:

```
import pymei

cmn_meidoc = pymei.documentFromFile("TestFiles/Fauv/fauvel_nous.mei").getMeiDocument()

from MEI_Translator import MensuralTranslation

mensural_meidoc = MensuralTranslation(cmn_meidoc, "antiqua", [["3", "p"], ["3", "p"], ["3", "p"]])
mensural_meidoc.getModifiedNotes('major semibreve')

```

The _"partial imperfection"_ modification only occurd in _Ars nova_ pieces. Here is an example:

```
import pymei

cmn_meidoc = pymei.documentFromFile("TestFiles/IvTrem/zodiacum.mei").getMeiDocument()

from MEI_Translator import MensuralTranslation

mensural_meidoc = MensuralTranslation(cmn_meidoc, "nova", [["i", "p", "i", "p"], ["i", "p", "i", "p"], ["i", "p", "i", "p"]])
mensural_meidoc.getModifiedNotes('partial imperfection')
```

### Getting the Mensural MEI File: the ```documentToFile``` function

Because the ```MensuralTranslated``` object is already instantiated, it behaves just like a regular MeiDocument. You can also edit any of the elements. To generate a file use the ```documentToFile``` function from the ```pymei``` module (already imported). To obtain the Mensural MEI file from your ```MensuralTranslated``` object ```mensural_meidoc``` use the following code:

```
pymei.documentToFile(mensural_meidoc)
```

You receive the same outcome as from the MEI\_Translator script, except that you are still able to modify the Mensural MEI document (with the ```MensuralTranslated``` object), and convert it to a file with ```pymei.documentToFile()```.

## Notes

<a name="one">1</a>: _Common Music Notation_ here refers to music notation in current use, aside from graphic music notation, and not the Lisp-based open-source music notation software.

<a name="two">2</a>: Alternatively, you could run the MEI\_Translator as a script on the command line to obtain the Mensural MEI file for this piece directly by entering: 
```python MEI_Translator.py TestFiles/IvTrem/bona.mei nova -NewVoiceN i p i p -NewVoiceN i p i p -NewVoiceN i i i p```

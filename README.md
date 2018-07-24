# MEI_Translator: from CMN-MEI to Mensural-MEI

The MEI_Translator script takes a CMN (Common Music Notation) [MEI](http://music-encoding.org) file and translates it into a Mensural MEI file.<sup>[1](#one)</sup> It was developed for mensural music that was transcribed in Sibelius, and exported to MEI files with the [sibmei](https://github.com/music-encoding/sibmei) plugin. MEI files generated with Sibelius are CMN-MEI files. The CMN-MEI module encodes music in contemporary notation. Compositions written in mensural notation should use the Mensural MEI module. The MEI Translator translates CMN-MEI files created with Sibelius to Mensural MEI files.

The Sibelius transcription of the pieces follows conventions developed by [Karen Desmond](https://www.brandeis.edu/facultyguide/person.html?emplid=5549ea5590219e2fd526777523c96d99ba7d1908). For further background on the project, see http://measuringpolyphony.org. The conventions followed for the modern transcriptions can be found in the 'About' page in the 'Encoding Process' section. In this section (third point) you can find the list of the articulation marks used to represent mensural notation features that are usually not represented in modern transcriptions (e.g., alterations and dots of division).

## Implementation
The CMN-MEI_to_MensuralMEI_Translator project has four modules: (1) arsantiqua, (2) arsnova, (3) white_notation, and (4) MEI_Translator. The first two modules contain functions that deal with features characteristic from one of the two medieval styles of notation: _ars antiqua_ and _ars nova_. The _arsnova_ module deals with "partial imperfections," and considers "minims" and "prolatio", while the _arsantiqua_ module considers the presence of "major semibreves" and "duplex longas." The third module deals with _white mensural_ notation. It is very similar to the _arsnova_ module, but it includes support for smaller note values (i.e., semiminima, fusa, and semifusas) and hemiola coloration, which were included in the late fourteenth century and were frequently used during the Renaissance.

The MEI_Translator module contains general functions for the translation, shared by the three _ars antiqua_, _ars nova_, and _white mensural_ styles. The user can run the module as a script, along with _piece name_, _music style_, and _mensuration value_ parameters.

## Requirements
### Software requirements
- The [LibMEI library](https://github.com/DDMAL/libmei). The wiki contains instructions on both the installation of the LibMEI C++ library, and the installation of the python bindings.
- The [SibMEI plugin](https://github.com/music-encoding/sibmei). Follow the _Download and Installation_ instructions of the README. The SibMEI plugin will allow you to export your Sibelius transcription of the piece into the CMN MEI that is used by the Mensural MEI Translator.
### Encoding requirements
- Follow the guidelines in http://measuringpolyphony.org regarding the use of articulation marks to represent certain mensural notation specificities that are usually not captured in modern transcriptions.
- If you are transcribing an _ars antiqua_ or an _ars nova_ piece, you need __to bar it by the long__ for the Mensural MEI Translator to work properly.
- If you are transcribing a _white mensural_ piece, you need to __bar it by the breve__ for the Mensural MEI Translator to work properly.

## Running the script
There are three types of parameters:
- the _piece name_, or the path to the piece if the composition is in a different directory than the script
- the _musical style_, three values: "ars_antiqua", "ars_nova", and "white_mensural"
- the _-voice_ flag, which is used to enter the mensuration of each voice. The mensuration values used with this flag depend on the _musical style_ of the piece (see following section).

### The -voice flag
Use this flag for each voice to enter its mensuration following the format: ```-voice <mensuration>```. The ```<mensuration>``` has two possible values depending of the style of your piece.

#### Ars antiqua mensuration values
If your piece is from the Ars Antiqua, your mensuration string should be two-characters long. The first character is a ```2``` or a ```3``` and it indicates the ```division of the breve``` (_duple_ or _triple division_, respectively). The second character is an ```i``` or a ```p``` and it indicates the modusminor (_imperfect_ or _perfect modusminor_, respectively).

##### Example
> ```-voice 3i``` indicates a voice with 3 minor semibreves (triple division) per breve and _imperfect modusminor_.

#### Ars nova and white notation mensuration values
If, on the other hand, you are dealing with an Ars nova or a white notation piece, your mensuration string should be four-characters long and must consist only of ```p``` and ```i``` chracters. These characters must be used in the following order to indicate the mensuration: _modusmajor_, _modusminor_, _tempus_, and _prolatio_. Medieval theorists would refer to ternary prolation as 'major' and a binary prolation as 'minor', but the labels 'p' and 'i' are continued for prolation, for simplicity's sake.

##### Example
> ```-voice ipip``` indicates a voice with _imperfect modusmajor_ and _tempus_, and _perfect modusminor_ and _prolatio_.

#### Changes in mensuration within a voice
To indicate changes in mensuration within a voice you must provide the measure number in which the mensuration change happens using the following format: 
> ```-voice <mensuration> <measure_number> <mensuration> <measure_number> <mensuration>``` and so on.

##### Example 
> ```-voice ippi 15 iipi 30 ipip``` indicates a voice that started in _imperfect modusmajor_, _perfect modusminor_, _perfect tempus_, and _minor prolation_. At measure 15, its _modusminor_ changes from _perfect_ to _imperfect_. At measure 30, the voice returns to its initial mensuration.

#### Multiple voices
The ```-voice``` flag is used for each voice in order to enter its mensuration. Therefore, the number of ```-voice``` flags must coincide with the number of voices in the CMN MEI file (and the Sibelius file). **IMPORTANT: The order in which you enter the mensuration of the voices using the ```-voice``` flags should be the same as the order of the voices in the CMN MEI file (or the Sibelius file).**

##### Examples

> ```-voice 2p —voice 2p —voice 2p -voice 3i 10 2p 20 3i 30 2p 40 3i```. Four-voice Ars antiqua piece. The lower voice starts with _imperfect modusminor_ and _triple division of the breve_, it changes to _perfect modusminor_ and _duple division of the breve_ at measure 10. It keeps switching between these two mensurations at measures 20, 30, and 40. The voice ends with the same mensuration it started. While all these changes in mensuration happen in the lower voice, the upper voices are constantly in _perfect modusminor_ and _duple division of the breve_.

> ```-voice ipii 25 iipp 40 ipii -voice ippi -voice ipii 25 iipp 40 ipii```. Three-voice Ars nova (or white mensural) piece. The upper and lower voices start with _imperfect modusmajor_, _perfect modusminor_, _imperfect tempus_, and _minor prolatio_. At measure 25, their _modusminor_ switch from _perfect_ to _imperfect_, while their tempus and prolatio switch from _imperfect_ to _perfect_. At measure 40, they return to their initial mensuration. While all these changes in mensuration happen in these two voices, the middle voice moves constantly in _imperfect modusmajor_, _perfect modusminor_, _perfect tempus_, and _minor prolatio_.

### Examples of running scripts in the command line

Here are two pieces, one for _ars nova_ and one for _ars antiqua_. The composition are included in this repository (_TestFiles_ directory).

_Ars nova_ piece - _Zodiacum_ from the IvTrem:

```
$ python MEI_Translator.py TestFiles/IvTrem/zodiacum.mei ars_nova -voice ipip -voice ipip -voice ipip
```

_Ars antiqua_ piece - _Fauvel_ from the Fauvel:

```
$ python MEI_Translator.py TestFiles/Fauv/fauvel.mei ars_antiqua -voice 3p -voice 3p -voice 3p
```

You can also go to the ```TestFiles``` directory and run:

```
$ python processing.py
```

The script above runs all the instructions contained in the ```IvTremPieces.txt``` and/or ```FauvPieces.txt``` files, which run the MEI\_Translator over all the pieces in the ```IvTrem``` and/or ```Fauv``` directories, respectively.

## Using the module
We saw in the previous section how to run the MEI\_Translator as a script. But the MEI\_Translator can also be used as a module.

Here are the steps to follow in order to use the MEI\_Translator as a module. To illustrate each step we are using ```bona.mei``` from the ```IvTrem``` as an input file.<sup>[2](#two)<sup>

1) On your python shell, import the ```pymei``` module and convert your piece into a ```pymei.MeiDocument``` object.

```
import pymei

cmn_meidoc = pymei.documentFromFile("TestFiles/IvTrem/bona.mei").getMeiDocument()
```

2) Import the ```MEI_Translator``` module and create a ```MensuralTranslation``` object, which will inherit all the methods from the ```pymei.MeiDocument``` class.

```
from MEI_Translator import MensuralTranslation`

mensural_meidoc = MensuralTranslation(cmn_meidoc, "ars_nova", [["ipip"], ["ipip"], ["iiip"]])
```

Now you will be able to use all the ```pymei.MeiDocument``` methods (```getElementsByName```, ```getElementById```, etc.) and a new method included in the ```MensuralTranslation``` class (```getModifiedNotes```) to be able to access elements in the file and edit them before you call the function ```documentToFile``` to create the file containing the Mensural MEI document.

### ```MeiDocument``` inherited methods:

We can use the inherited methods from ```pymei.MeiDocument``` to check that certain _MEI elements_ were actually removed in the translation process, like the ```tie``` and ```mRest``` elements. Mensural notation does not use ties and, as it doesn't have measures, the Mensural-MEI module doesn't recognize ```mRest``` elements (measure rests). We can check if the ```tie``` elements present in the CMN-MEI document are still present in the Mensural MEI document by using:

```
cmn_meidoc.getElementsByName('tie')
mensural_meidoc.getElementsByName('tie')
```

The second instruction returns a blank list. Same thing will happen with the ```mRest``` elements. Actually, the script converts all ```mRest``` elements into simple ```rest``` elements; you can verify this by using the following code (which should return ```True```):

```
len(cmn_meidoc.getElementsByName('rest')) + len(cmn_meidoc.getElementsByName('mRest')) == len(mensural_meidoc.getElementsByName('rest'))
```

### Additional methods:

The ```getModifiedNotes()``` method returns a list of notes that have been modified from its default value (the value given by the mensuration). There are only 5 possible modifications: _"imperfection"_, _"alteration"_, _"perfection"_, _"partial imperfection"_ or _"major semibreve"_. You can pass any of these five string-values as a parameter to the method ```getModifiedNotes()``` in order to get the list of notes from the piece with this particular modification; or you can omit the parameter and get a list of all notes modified by any of these five modification types.

Since _"major semibreve"_ is a modification that occurs only in _ars antiqua_, you could run the following code to see the method working:

```
import pymei

cmn_meidoc = pymei.documentFromFile("TestFiles/Fauv/fauvel.mei").getMeiDocument()

from MEI_Translator import MensuralTranslation

mensural_meidoc = MensuralTranslation(cmn_meidoc, "ars_antiqua", [["3p"], ["3p"], ["3p"]])
mensural_meidoc.getModifiedNotes('major semibreve')

```

The _"partial imperfection"_ modification only occurs in _ars nova_ (and _white mensural_) pieces. Here is an example:

```
import pymei

cmn_meidoc = pymei.documentFromFile("TestFiles/IvTrem/zodiacum.mei").getMeiDocument()

from MEI_Translator import MensuralTranslation

mensural_meidoc = MensuralTranslation(cmn_meidoc, "ars_nova", [["ipip"], ["ipip"], ["ipip"]])
mensural_meidoc.getModifiedNotes('partial imperfection')
```

### Getting the Mensural MEI File: the ```documentToFile``` function

Because the ```MensuralTranslation``` object is already instantiated, it behaves just like a regular MeiDocument. You can also edit any of the elements. To generate a file use the ```documentToFile``` function from the ```pymei``` module (already imported). To obtain the Mensural MEI file from your ```MensuralTranslation``` object ```mensural_meidoc``` use the following code:

```
pymei.documentToFile(mensural_meidoc)
```

You receive the same outcome as from the MEI\_Translator script, except that you are still able to modify the Mensural MEI document (with the ```MensuralTranslation``` object), and convert it to a file with ```pymei.documentToFile()```.

## Notes

<a name="one">1</a>: _Common Music Notation_ here refers to music notation in current use, aside from graphic music notation, and not the Lisp-based open-source music notation software.

<a name="two">2</a>: Alternatively, you could run the MEI\_Translator as a script on the command line to obtain the Mensural MEI file for this piece directly by entering: 
```
python MEI_Translator.py TestFiles/IvTrem/bona.mei ars_nova -voice ipip -voice ipip -voice iiip
```

"""
MEI_Translator Module
Translate a CMN-MEI document to a Mensural-MEI document.

Functions:
separate_staves_per_voice -- Return a list of lists, each sublist contains all the <staff> elements for a particular voice.
merge_ties -- Merge tied-notes into one and return the lists of <note> elements that shouldn't be included in the Mensural MEI file based on this.
remove_non_mensural_attributes -- Remove/Replace attributes from <note> and <rest> that are not part of the Mensural-MEI schema.

Classes:
MensuralTranslation -- Create the translated Mensural-MEI document.
"""
import argparse

from pymei import documentFromFile, documentToFile, MeiDocument, MeiElement

import white_notation
import arsnova
import arsantiqua


def separate_staves_per_voice(doc):
    """Return a list of lists, each of which contains all the <staff> elements of a voice in the pymei.MeiDocument object.

    Arguments:
    doc -- the pymei.MeiDocument object to be translated to Mensural-MEI
    """
    num_voices = len(doc.getElementsByName('staffDef'))
    all_voices = []
    measures = doc.getElementsByName('measure')
    for i in range(0, num_voices):
        ind_voice = []
        for measure in measures:
            staves_in_measure = measure.getChildrenByName('staff')
            staff_i = staves_in_measure[i]
            ind_voice.append(staff_i)
        all_voices.append(ind_voice)

    return all_voices


def merge_ties(doc):
    """Join into one the notes that are tied together in the pymei.MeiDocument object.

    Set the @dur of the first note of the tied notes to the value 'TiedNote!'.
    And set its @dur.ges (perform3ed duration) to the sum of the performed duration of the individual notes that make up the tie.
    Return a list of the other notes that make up the tie (the ones after the first), which shouldn't be included in the output file.

    Arguments:
    doc -- the pymei.MeiDocument object to be translated to Mensural-MEI
    """
    ids_removeList = []
    ties_list = doc.getElementsByName('tie')
    for i in range (len(ties_list)-1, -1, -1):
        tie = ties_list[i]

        # Start note
        startid = tie.getAttribute('startid').value
        note_startid = startid[1:]  # Removing the '#' character from the startid value, to have the id of the note
        start_note = doc.getElementById(note_startid)
        start_dur = start_note.getAttribute('dur').value    # Value of the form: 'long', 'breve', '1' or '2'
        start_durGes_number = int(start_note.getAttribute('dur.ges').value[:-1])    # Value of the form: 1024

        # End note
        endid = tie.getAttribute('endid').value
        note_endid = endid[1:]
        end_note = doc.getElementById(note_endid)
        end_dur = end_note.getAttribute('dur').value
        end_durGes_number = int(end_note.getAttribute('dur.ges').value[:-1])

        # Calculation of the @dur.ges
        durGes_number = start_durGes_number + end_durGes_number
        durGes = str(durGes_number) + "p"
        start_note.getAttribute('dur.ges').setValue(durGes)
        ids_removeList.append(end_note.id)

        # Sets @dur = 'TiedNote!'
        start_note.getAttribute('dur').setValue('TiedNote!')

    return ids_removeList


def remove_non_mensural_attributes(doc):
    """Remove/Replace attributes inside <note> and <rest> elments on the pymei.MeiDocument object, that are not part of the Mensural-MEI schema.

    Arguments:
    doc -- the pymei.MeiDocument object to be translated to Mensural-MEI
    """
    notes = doc.getElementsByName('note')
    for note in notes:
        # Remove extraneous attributes in the <note> element
        if note.hasAttribute('layer'):
            note.removeAttribute('layer')
        if note.hasAttribute('pnum'):
            note.removeAttribute('pnum')
        if note.hasAttribute('staff'):
            note.removeAttribute('staff')
        if note.hasAttribute('stem.dir'):
            note.removeAttribute('stem.dir')
        if note.hasAttribute('dots'):
            note.removeAttribute('dots')
        # Replace extraneous attributes by the appropriate mensural attributes in the <note> element:
        # For plicas
        if note.hasAttribute('stem.mod'):
            stemmod = note.getAttribute('stem.mod')
            if stemmod.value == "1slash":
                note.addAttribute('plica', 'desc')
                note.removeAttribute('stem.mod')
            elif stemmod.value == "2slash":
                note.addAttribute('plica', 'asc')
                note.removeAttribute('stem.mod')
            else:
                pass
        # Articulations changes
        if note.hasAttribute('artic'):
            artic = note.getAttribute('artic')
            if artic.value == "stacc":
                note.removeAttribute('artic')
            elif artic.value == "ten":
                note.addAttribute('stem.dir', 'down') # If the note has this attribute (@stem.dir) already, it overwrites its value
                note.removeAttribute('artic')
    # Remove @dots from <rest> elements
    rests = doc.getElementsByName('rest')
    for rest in rests:
        if rest.hasAttribute('dots'):
            rest.removeAttribute('dots')


def num(mensurationString):
    """Transform the characters 'p' and 'i' to the values '3' and '2', respectively, and return the appropriate numeric value.

    Arguments:
    mensurationString -- one-character string with two possible values: 'i' or 'p'
    """
    strings_for_mensuration = ['p', 'i']
    numbers_for_mensuration = ['3', '2']
    mensurationNumber = numbers_for_mensuration[strings_for_mensuration.index(mensurationString)]
    return mensurationNumber


class MensuralTranslation(MeiDocument):
    """Translate a CMN-MEI document to a Mensural-MEI document.

    MensuralTranslation is a subclass of MeiDocument. It inherits all its methods, without any modification to any of them. 
    The constructor is the only extended method, as not only the MeiDocument which would contain the Mensural-translation is created here, but also the translation process itself is done here. 
    And there is only one additional method (getModifiedNotes) to deal with the peculiarities of mensural notation.
    
    Methods:
    getModifiedNotes -- gets a list of notes which value has been modified from the original (the default value given by the mensuration)
    """

    def __init__(self, cmn_meidoc, ars_type, mensuration_list):
        """Create the Mensural-MEI document that contains the translation of the CMN-MEI document.

        Arguments:
        cmn_meidoc -- the pymei.MeiDocument object that contains the CMN-MEI document intended to be translated to Mensural-MEI
        ars_type -- string that indicates if the piece belongs to the Ars Nova or the Ars Antiqua repertoire. It has two values: 'nova' or 'antiqua'
        mensuration_list -- list in which each element is a list that encodes the mensuration for each voice.
        For Ars Nova each sublist has 4 elements (with values 'p' or 'i') that indicate the mensuration of the voice (in the order: modusmaior, modusminor, tempus and prolatio).
        For Ars Antiqua each sublist has 2 elemnts (the first is '3' or '2' -indicating the division of the breve-, and the second is 'p' or 'i' -indicating the modusminor-).
        """
        # Getting necessary information from the input (CMN-MEI) file
        all_voices = separate_staves_per_voice(cmn_meidoc)
        ids_removeList = merge_ties(cmn_meidoc)

        # Output (Mensural-MEI) file Part:
        MeiDocument.__init__(self)
        self.root = cmn_meidoc.getRootElement()

        # ScoreDef Part of the <score> element:
        out_scoreDef = MeiElement('scoreDef')
        # Make it share the id (@xml:id) it has in the input file
        out_scoreDef.id = cmn_meidoc.getElementsByName('scoreDef')[0].id
        # Add as its child the <staffGrp> element, with all the <staffDef> elements and the right mensuration (@modusmaior, @modusminor, @tempus and @prolatio) for each one
        out_staffGrp = cmn_meidoc.getElementsByName('staffGrp')[-1]
        # The [-1] guarantees that the <staffGrp> element taken is the one which contains the <staffDef> elements (previous versions of the plugin stored a <staffGrp> element inside another <staffGrp>)
        stavesDef = out_staffGrp.getChildren()
        # Mensuration added to the staves definition <staffDef>
        # -> For the new notation (ars nova or white mensural)
        if ars_type in ["ars_nova", "white_mensural"]:
            for i in range(0, len(stavesDef)):
                voice_staffDef = stavesDef[i]
                voice_mensuration = mensuration_list[i]
                voice_staffDef.addAttribute('modusmaior', num(voice_mensuration[0]))
                voice_staffDef.addAttribute('modusminor', num(voice_mensuration[1]))
                voice_staffDef.addAttribute('tempus', num(voice_mensuration[2]))
                voice_staffDef.addAttribute('prolatio', num(voice_mensuration[3]))
        # -> For the old notation (ars antiqua)
        else:
            for i in range(0, len(stavesDef)):
                voice_staffDef = stavesDef[i]
                voice_mensuration = mensuration_list[i]
                voice_staffDef.addAttribute('modusmaior', '2')
                voice_staffDef.addAttribute('modusminor', num(voice_mensuration[1]))
                voice_staffDef.addAttribute('tempus', voice_mensuration[0])
        out_scoreDef.addChild(out_staffGrp)

        # Section Part of the <score> element:
        out_section = MeiElement('section')
        out_section.id = cmn_meidoc.getElementsByName('section')[0].id

        # Add the new <scoreDef> and empty <section> elements to the <score> element after cleaning it up
        score = self.getElementsByName('score')[0]
        score.deleteAllChildren()
        score.addChild(out_scoreDef)
        score.addChild(out_section)

        # Fill the section element with the information of each voice (contained in all_voices)
        # -> For white notation
        if ars_type == "white_mensural":
            tuplet_minims = white_notation.fill_section(out_section, all_voices, ids_removeList, cmn_meidoc)
            staffDefs = self.getElementsByName('staffDef')
            staves = self.getElementsByName('staff')
            for i in range(0, len(staffDefs)):
                staffDef = staffDefs[i]
                modusmaior = int(staffDef.getAttribute('modusmaior').value)
                modusminor = int(staffDef.getAttribute('modusminor').value)
                tempus = int(staffDef.getAttribute('tempus').value)
                prolatio = int(staffDef.getAttribute('prolatio').value)

                notes_per_voice = staves[i].getChildrenByName('layer')[0].getChildrenByName('note')
                rests_per_voice = staves[i].getChildrenByName('layer')[0].getChildrenByName('rest')

                white_notation.noterest_to_mensural(notes_per_voice, rests_per_voice, modusmaior, modusminor, tempus, prolatio, tuplet_minims)
        # -> For ars nova
        elif ars_type == "ars_nova":
            tuplet_minims = arsnova.fill_section(out_section, all_voices, ids_removeList, cmn_meidoc)
            staffDefs = self.getElementsByName('staffDef')
            staves = self.getElementsByName('staff')
            for i in range(0, len(staffDefs)):
                staffDef = staffDefs[i]
                modusmaior = int(staffDef.getAttribute('modusmaior').value)
                modusminor = int(staffDef.getAttribute('modusminor').value)
                tempus = int(staffDef.getAttribute('tempus').value)
                prolatio = int(staffDef.getAttribute('prolatio').value)

                notes_per_voice = staves[i].getChildrenByName('layer')[0].getChildrenByName('note')
                rests_per_voice = staves[i].getChildrenByName('layer')[0].getChildrenByName('rest')

                arsnova.noterest_to_mensural(notes_per_voice, rests_per_voice, modusmaior, modusminor, tempus, prolatio, tuplet_minims)
        # -> For ars antiqua
        else:
            breve = mensuration_list[0][0]
            voices_elements = arsantiqua.fill_section(out_section, all_voices, ids_removeList, cmn_meidoc, breve)
            staffDefs = self.getElementsByName('staffDef')
            staves = self.getElementsByName('staff')
            for i in range(0, len(staffDefs)):
                staffDef = staffDefs[i]
                modusminor = int(staffDef.getAttribute('modusminor').value)

                notes_per_voice = staves[i].getChildrenByName('layer')[0].getChildrenByName('note')
                rests_per_voice = staves[i].getChildrenByName('layer')[0].getChildrenByName('rest')
                elements_per_voice = voices_elements[i]

                arsantiqua.noterest_to_mensural(notes_per_voice, rests_per_voice, modusminor)

                if staffDef.getAttribute('tempus').value == '3':
                    arsantiqua.sb_major_minor(elements_per_voice)
                else:
                    pass

        remove_non_mensural_attributes(self)

    def getModifiedNotes(self, modification_type=None):
        """Return a list of tuplets that indicate the note and the modification it has experienced from its default value.

        Arguments:
        modification_type -- string with 5 possible values: 'alteration', 'imperfection', 'perfection', 'partial imperfection', 'major semibreve'. (Default value: None)

        Return:
        List of tuplets. 
        First element of the tuplet indicates a note that has been modified from its default value (the value given by the mensuration).
        Second element indicates the modification that note has experienced ('i' for imperfection, 'a' for alteration, 'p' for perfection, etc).
        """
        if modification_type is None:
            modifications_list = ['i', 'a', 'p', 'major', 'immediate_imp', 'remote_imp', 'imperfection + immediate_imp', 'imperfection + remote_imp']
        elif modification_type == "alteration":
            modifications_list = ['a']
        elif modification_type == "imperfection":
            modifications_list = ['i']
        elif modification_type == "perfection":
            modifications_list = ['p']
        elif modification_type == "partial imperfection":
            modifications_list = ['immediate_imp', 'remote_imp', 'imperfection + immediate_imp', 'imperfection + remote_imp']
        elif modification_type == "major semibreve":
            modifications_list = ['major']
        else:
            return "Invalid argument. The argument modification_type can only have the following 5 values: 'alteration', 'imperfection', 'perfection', 'partial imperfection' and 'major semibreve'; or no-arguments at all."

        notes = self.getElementsByName('note')
        all_modified_notes = []
        for note in notes:
            if note.hasAttribute("quality") and (note.getAttribute("quality").value in modifications_list):
                all_modified_notes.append((note, note.getAttribute("quality")))

        return all_modified_notes


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('piece', help="If the CMN-MEI file of the piece is in the same directory as the MEI_Translator module, just enter the 'name' of the piece (including its extension: '.mei'). If not, insert the whole 'path' of the piece.")
    parser.add_argument('style', choices=['ars_antiqua', 'ars_nova', 'white_mensural'], help="This indicates the style of the piece, whether it belongs to the 'ars antiqua', 'ars nova', or 'white notation' repertoire. If you select 'ars_nova' or 'white_mensural' you have to use the optional argument '-NewVoiceN' to add the mensuration (values for: modusmajor, modusminor, tempus, and prolatio) for each voice. If you choose 'ars_antiqua' you have to use the optional argument '-NewVoiceA' to add the mensuration (values for: breve and modusminor) for each voice.")
    parser.add_argument('-NewVoiceA', nargs=2, action='append', choices=['3','2', 'p', 'i'], help="Use this flag for each new voice (in ars antiqua) that you are entering. After the flag, use '2' or '3' to indicate the 'division of the breve' (duple of triple division) and then use 'p' or 'i' to indicate the 'modusminor'. The order in which you enter the mensuration of the voices here should be the same as the order of the voices in the CMN-MEI file. \nExample for an Ars Antiqua 4-voice motet with 3 minor semibreves per breve and imperfect modus: -NewVoiceA 3 i -NewVoiceA 3 i -NewVoiceA 3 i -NewVoiceA 3 i") # for now, you have to add each voice
    parser.add_argument('-NewVoiceN', nargs=4, action='append', choices=['p', 'i'], help="Use this flag for each new voice (in ars nova or in white mensural notation) that you are entering. After the flag, use 'p' or 'i' to indicate the mensuration (in the order: modusmajor + modusminor + tempus + prolatio). The order in which you enter the mensuration of the voices here should be the same as the order of the voices in the CMN-MEI file. \nExample for an Ars Nova 3-voice motet with different mensurations for each voice: -NewVoiceN i i p p -NewVoiceN i p i p -NewVoiceN p i i i") # for now, just 4 values per voice are allowed
    args = parser.parse_args()

    # Parser errors:
    # Case: ars nova or white mensural notation
    if args.style in ['ars_nova', 'white_mensural']:
        # Inconsistency between the style argument and the NewVoice flag used
        if args.NewVoiceA is not None:
            parser.error("Use of incorrect 'NewVoice' flag. For 'ars nova' and 'white mensural' use exclusively -NewVoiceN flag to add the mensuration information of each voice. \nSee the 'help' for more information: 'python MEI_Translator.py -h'")
        # Missing information of the mensuration of the voices
        if args.NewVoiceN is None:
            parser.error("No voice mensuration information has been provided. Use the flag -NewVoiceN to add the mensuration information for each voice. \nSee the 'help' for more information: 'python MEI_Translator.py -h'")
        else:
            mensurationList = args.NewVoiceN
    # Case: ars antiqua
    else:
        # Inconsistency between the style argument and the NewVoice flag used
        if args.NewVoiceN is not None:
            parser.error("Use of incorrect 'NewVoice' flag. For 'ars antiqua' use exclusively -NewVoiceA flag to add the mensuration information of each voice. \nSee the 'help' for more information: 'python MEI_Translator.py -h'")
        # Missing information of the mensuration of the voices
        if args.NewVoiceA is None:
            parser.error("No voice mensuration information has been provided. Use the flag -NewVoiceA to add the mensuration information for each voice. \nSee the 'help' for more information: 'python MEI_Translator.py -h'")
        else:
            mensurationList = args.NewVoiceA
        # Wrong argument for 'breve division' (first argument of -NewVoiceA) in ars antiqua
        for voice in args.NewVoiceA:
            breve_division = voice[0]
            if breve_division not in ['3', '2']:
                parser.error("Use of invalid arguments for -NewVoiceA. First argument (breve division) should be '3' or '2' (triple or duple).")
            else:
                pass
    # Case: the numer of voices entered by the user is smaller/larger than the number of voices in the piece
    print(args.piece)
    input_doc = documentFromFile(args.piece).getMeiDocument()
    stavesDef = input_doc.getElementsByName('staffDef')
    if len(mensurationList) < len(stavesDef):
        parser.error("The number of voices entered (amount of 'NewVoice' flags) is smaller than the number of voices on the CMN-MEI file of the piece.")
    elif len(mensurationList) > len(stavesDef):
        parser.error("The number of voices entered (amount of 'NewVoice' flags) is larger than the number of voices on the CMN-MEI file of the piece.")
    else:
        pass

    # Translation step: use of the MensuralMeiTranslatedDocument class
    mensural_meidoc = MensuralTranslation(input_doc, args.style, mensurationList)
    documentToFile(mensural_meidoc, args.piece[:-4] + "_MENSURAL.mei")

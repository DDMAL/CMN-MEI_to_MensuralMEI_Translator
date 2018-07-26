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
import itertools

from pymei import documentFromFile, documentToFile, MeiDocument, MeiElement

import white_notation
import arsnova
import arsantiqua


def separate_staves_per_voice(doc):
    """Return a list of lists, each of which contains all the <staff> elements of a voice 
    (which are children of different <measure> elements) in the pymei.MeiDocument object.

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
    for i in range(len(ties_list)-1, -1, -1):
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
                note.addAttribute('stem.dir', 'down')  # If the note has this attribute (@stem.dir) already, it overwrites its value
                note.removeAttribute('artic')
    # Remove @dots from <rest> elements
    rests = doc.getElementsByName('rest')
    for rest in rests:
        if rest.hasAttribute('dots'):
            rest.removeAttribute('dots')


class MensuralTranslation(MeiDocument):
    """Translate a CMN-MEI document to a Mensural-MEI document.

    MensuralTranslation is a subclass of MeiDocument. It inherits all its methods, without any modification to any of them.
    The constructor is the only extended method, as not only the MeiDocument which would contain the Mensural-translation is created here, but also the translation process itself is done here. 
    And there is only one additional method (getModifiedNotes) to deal with the peculiarities of mensural notation.

    Methods:
    getModifiedNotes -- gets a list of notes which value has been modified from the original (the default value given by the mensuration)
    """

    def __init__(self, cmn_meidoc, ars_type, piece_mensuration):
        """Create the Mensural-MEI document that contains the translation of the CMN-MEI document.

        Arguments:
        cmn_meidoc -- the pymei.MeiDocument object that contains the CMN-MEI document intended to be translated to Mensural-MEI
        ars_type -- string that indicates if the piece belongs to the Ars Nova or the Ars Antiqua repertoire. It has two values: 'nova' or 'antiqua'
        piece_mensuration -- dictionary in which each element is a list that encodes the mensuration for each voice.
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
            for i, voice_staffDef in enumerate(stavesDef):
                voice_mensuration_changes = piece_mensuration[i]
                voice_initial_mensuration = voice_mensuration_changes['1']
                voice_staffDef.addAttribute('modusmaior', voice_initial_mensuration[0])
                voice_staffDef.addAttribute('modusminor', voice_initial_mensuration[1])
                voice_staffDef.addAttribute('tempus', voice_initial_mensuration[2])
                voice_staffDef.addAttribute('prolatio', voice_initial_mensuration[3])
                voice_staffDef.addAttribute('notationtype', "mensural")
        # -> For the old notation (ars antiqua)
        else:
            for i, voice_staffDef in enumerate(stavesDef):
                voice_mensuration_changes = piece_mensuration[i]
                voice_initial_mensuration = voice_mensuration_changes['1']
                voice_staffDef.addAttribute('modusmaior', '2')
                voice_staffDef.addAttribute('modusminor', voice_initial_mensuration[1])
                voice_staffDef.addAttribute('tempus', voice_initial_mensuration[0])
                voice_staffDef.addAttribute('notationtype', "mensural")
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
            tuplet_minims = white_notation.fill_section(out_section, all_voices, ids_removeList, cmn_meidoc, piece_mensuration)
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
            tuplet_minims = arsnova.fill_section(out_section, all_voices, ids_removeList, cmn_meidoc, piece_mensuration)
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
            voices_elements = arsantiqua.fill_section(out_section, all_voices, ids_removeList, cmn_meidoc, breve, piece_mensuration)
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

    # User input
    parser = argparse.ArgumentParser()
    parser.add_argument('piece', help="If the CMN-MEI file of the piece is in the same directory as the MEI_Translator module, just enter the 'name' of the piece (including its extension: '.mei'). If not, insert the whole 'path' of the piece.")
    parser.add_argument('style', choices=['ars_antiqua', 'ars_nova', 'white_mensural'], help="This indicates the style of the piece, whether it belongs to the 'ars antiqua', 'ars nova', or 'white notation' repertoire.")
    parser.add_argument('-voice', nargs='+', action='append', help="Use this flag for each voice to enter its mensuration in the following format: -voice <mensuration>. \nThe mensuration string has two possible values depending of the style of your piece.\n-If your piece is from the Ars Antiqua, your mensuration string should be two chracters long, the first character is a '2' or a '3' and indicates  the 'division of the breve' (duple or triple division), and the second character is an 'i' or 'p' and it indicates the modusminor (imperfect or perfect modusminor). \nExample for an Ars Antiqua 3-voice piece with 2 minor semibreves per breve and perfect modus: -voice 2p -voice 2p -voice 2p \n-If, on the other hand, you are dealing with an Ars nova or a white notation piece, your mensuration string is four characters long and it is composed only of 'p' and 'i' chracters. These characters must be used to indicate the mensuration in the following order: modusmajor, modusminor, tempus, and prolatio. \nExample of a two-voice Ars nova (or white mensural) piece with different mensuration in each voice: -voice ippi -voice iipp. Both voices are in imperfect modusmajor, the upper one has perfect modus and tempus with minor prolatio, while the lower one is in imperfect modus, perfect tempus and major prolatio. \n\nTo indicate changes in mensuration within a voice you must provide the measure number in which the mensuration change happens using the following format: -voice <mensuration> <measure_number> <mensuration> <measure_number> <mensuration> and so on.\nExample: '-voice ipip 15 ippp 30 ipip -voice ipii -voice ipii'. In this example the first voice starts in imperfect modusmajor, perfect modusminor, imperfect tempus, and major prolatio. At measure 15th, its tempus changes from imperfect to perfect. Finally, it comes gack to imperfect tempus at measure 30th. While all these changes in mensuration happens in the uppper voice, the two lower voices move always in imperfect modusmajor, perfect modusminor and imperfect tempus with minor prolatio. \n\nThe order in which you enter the mensuration of the voices here should be the same as the order of the voices in the CMN-MEI file.")
    args = parser.parse_args()

    # All possible choices of mensuration for ars antiqua and ars nova pieces
    choices_antiq = [breve+modus for modus in 'ip' for breve in '32']
    choices_nova = [''.join(i) for i in itertools.product(['i', 'p'], repeat=4)]

    # Choices depending on the style chosen by the user
    if args.style == 'ars_antiqua':
        choices = choices_antiq
    else:
        choices = choices_nova

    # Evaluating the user input
    for i, voice in enumerate(args.voice):
        measures = voice[1::2]
        mensurations = voice[0::2]

        # 1. Error in Measure number (it is not an integer)
        try:
            [int(m) for m in measures]
        except:
            parser.error("There is a wrong measure number in voice # " + str(i+1))

        # 2. Error in mensuration (it is not any of the available choices for ars antiqua or nova)
        if all([mensur in choices for mensur in mensurations]) is False:
            parser.error("There is a wrong mensuration in voice # " + str(i+1) + ".\nPlease follow the instructions regarding how to write the mensuration for " + args.style + " pieces.")
    
    # If everything is fine, save the list of mensurations
    mensuration_list = args.voice

    # 3. Error in the number of voices entered (it is smaller/larger than the number of voices in the piece)
    print(args.piece)
    input_doc = documentFromFile(args.piece).getMeiDocument()
    stavesDef = input_doc.getElementsByName('staffDef')
    if len(mensuration_list) < len(stavesDef):
        parser.error("The number of voices entered (amount of '-voice' flags) is smaller than the number of voices on the CMN-MEI file of the piece.")
    elif len(mensuration_list) > len(stavesDef):
        parser.error("The number of voices entered (amount of '-voice' flags) is larger than the number of voices on the CMN-MEI file of the piece.")
    else:
        pass

    # Just for visualization purposes:
    print(args.voice)
    
    
    # Reformatting of the mensuration information for whole piece:
    # Changing the mensuration list given by the user to a dictionary that indicates the mensuration changes 
    # for each voice in a form easier to deal with according to the Mensural MEI schema.

    # 1. Adding the measure number ('1') for the first mensuration indicated by the user for each voice
    for i, item in enumerate(mensuration_list):
        mensuration_list[i] = ['1'] + item
    # 2. Rewriting the mensuration list given by the user as a dictionary that indicates the mensuration changes for each voice
    piece_mensuration = {}
    for i, item in enumerate(mensuration_list):
        voice_mensuration_changes = dict(zip(item[0::2], item[1::2]))
        piece_mensuration[i] = voice_mensuration_changes
    # Example:    piece_mensuration = {0: {'1': 'ipip'}, 1: {'1': 'ipip'}, 2: {'1': 'ipip', '33': 'ippp'}}
    # Each entry of the piece_mensuration dictionary is a key-value consisting of:
    # - The voice number as the key, and
    # - A dictionary of the mensuration changes of that voice as its value. 
    # Consider the entry for the last voice:    2: {'1': 'ipip', '33': 'ippp'}
    # The dictionary shows the changes of mensuration within that voice. The keys indicate the measure where
    # the mensuration change happens, and the value indicates the actual mensuration. 
    # So for this entry, the initial mensuration (at measure 1) is given by 'ipip',
    # which changes at measure 33 to 'ippp'.

    # 3. Change the mensuration dictionary, so that the mensuration values are consistent with the way in
    # which MEI encodes the modus major, modus minor, tempus, and prolatio
    # Changing entries as 'ippp' to a list of the form ['2', '3', '3', '3'] that encodes the individual
    # values for the attributes @modusmaior, @modusminor, @tempus, and @prolatio, respectively
    numvalue = {'p': '3', '3': '3', 'i': '2', '2': '2'}
    for voice_num in piece_mensuration:
        voice_mensuration_changes = piece_mensuration[voice_num]
        for measure_num in voice_mensuration_changes:
            current_mensuration = voice_mensuration_changes[measure_num]
            piece_mensuration[voice_num][measure_num] = [numvalue[mensur_note_level] for mensur_note_level in list(current_mensuration)]

    # Translation step: use of the MensuralMeiTranslatedDocument class
    mensural_meidoc = MensuralTranslation(input_doc, args.style, piece_mensuration)
    documentToFile(mensural_meidoc, args.piece[:-4] + "_MENSURAL.mei")

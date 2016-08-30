from pymei import *
import arsnova
import arsantiqua
import argparse

def separate_staves_per_voice(doc):
    """Return a list of lists, each of which contains all the <staff> elements of a voice in the MeiDocument (doc)."""
    num_voices = len(doc.getElementsByName('staffDef'))
    all_voices = []
    for i in range(0, num_voices):
        measures = doc.getElementsByName('measure')
        ind_voice = []
        for measure in measures:
            staves_in_measure = measure.getChildrenByName('staff')
            staff_i = staves_in_measure[i]
            ind_voice.append(staff_i)
        all_voices.append(ind_voice)

    return all_voices

def merge_ties(doc):
    """Join into one the notes that are tied together in the MeiDocument (doc)

    Set the @dur of the first note of the tied notes to the value 'TiedNote!'
    And set its @dur.ges (perform3ed duration) to the sum of the performed duration of the individual notes that make up the tie
    Return a list of the other notes that make up the tie (the ones after the first), which shouldn't be included in the output file"""
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

def remove_CMNattributes(doc):
    # Remove/Replace extraneous attributes on the notes
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
                if not note.hasChildren('dot'):
                    note.addChild(MeiElement('dot'))
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
    strings_for_mensuration = ['p', 'i']
    numbers_for_mensuration = ['3', '2']
    mensurationNumber = numbers_for_mensuration[strings_for_mensuration.index(mensurationString)]
    return mensurationNumber


class MensuralMeiTranslatedDocument(MeiDocument):

    def __init__(self, input_doc, all_voices, ids_removeList, ars_type, mensuration_list):
        self.output_doc = MeiDocument()
        self.output_doc.root = input_doc.getRootElement()

        # ScoreDef Part of the <score> element:
        out_scoreDef = MeiElement('scoreDef')
        # Make it share the id (@xml:id) it has in the input file
        out_scoreDef.id = input_doc.getElementsByName('scoreDef')[0].id
        # Add as its child the <staffGrp> element, with all the <staffDef> elements and the right mensuration (@modusmaior, @modusminor, @tempus and @prolatio) for each one
        out_staffGrp = input_doc.getElementsByName('staffGrp')[-1]
        # The [-1] guarantees that the <staffGrp> element taken is the one which contains the <staffDef> elements (previous versions of the plugin stored a <staffGrp> element inside another <staffGrp>)
        stavesDef = out_staffGrp.getChildren()
        # Mensuration added to the staves definition <staffDef>
        if ars_type == "ArsNova":
            for i in range(0, len(stavesDef)):
                voice_staffDef = stavesDef[i]
                voice_mensuration = mensuration_list[i]
                voice_staffDef.addAttribute('modusmaior', num(voice_mensuration[0]))
                voice_staffDef.addAttribute('modusminor', num(voice_mensuration[1]))
                voice_staffDef.addAttribute('tempus', num(voice_mensuration[2]))
                voice_staffDef.addAttribute('prolatio', num(voice_mensuration[3]))
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
        out_section.id = input_doc.getElementsByName('section')[0].id

        # Add the new <scoreDef> and empty <section> elements to the <score> element after cleaning it up
        score = self.output_doc.getElementsByName('score')[0]
        score.deleteAllChildren()
        score.addChild(out_scoreDef)
        score.addChild(out_section)

        # Fill the section element with the information of each voice (contained in all_voices)
        if ars_type == "ArsNova":
            tuplet_minims = arsnova.fill_section(out_section, all_voices, ids_removeList, input_doc)
            staffDefs = self.output_doc.getElementsByName('staffDef')
            staves = self.output_doc.getElementsByName('staff')
            for i in range(0, len(staffDefs)):
                staffDef = staffDefs[i]
                modusmaior = int(staffDef.getAttribute('modusmaior').value)
                modusminor = int(staffDef.getAttribute('modusminor').value)
                tempus = int(staffDef.getAttribute('tempus').value)
                prolatio = int(staffDef.getAttribute('prolatio').value)
                
                notes_per_voice = staves[i].getChildrenByName('layer')[0].getChildrenByName('note')
                rests_per_voice = staves[i].getChildrenByName('layer')[0].getChildrenByName('rest')

                arsnova.noterest_to_mensural(notes_per_voice, rests_per_voice, modusmaior, modusminor, tempus, prolatio, tuplet_minims)
        else:
            breve = mensuration_list[0][0]
            voices_elements = arsantiqua.fill_section(out_section, all_voices, ids_removeList, input_doc, breve)
            staffDefs = self.output_doc.getElementsByName('staffDef')
            staves = self.output_doc.getElementsByName('staff')
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

        remove_CMNattributes(self.output_doc)

    def toFile(self, filename):
        documentToFile(self.output_doc, filename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('piece', help="If the CMN-MEI file of the piece is in the same directory as the MEI_Translator module, just enter the 'name' of the piece (including its extension: '.mei'). If not, put the whole 'path' of the piece.")
    parser.add_argument('which_ars', choices=['ArsNova', 'ArsAntiqua'], help="If you select 'ArsNova' you have to use the optional argument '--newvoice_nova' to add the mensuration (values for: modusmajor, modusminor, tempus and prolatio) for each voice. If you choose 'ArsAntiqua' you have to use the optional argument '--newvoice_antiqua' to add the mensuration (values for: breve and modusminor) for each voice.")
    parser.add_argument('--newvoice_nova', nargs=4, action='append', choices=['p', 'i'], default=[], help="Use this flag for each new voice (in Ars Nova) that you are entering. After the flag, use 'p' or 'i' to indicate the mensuration (in the order: modusmajor + modusminor + tempus + prolatio). The order in which you enter the mensuration of the voices here should be the same as the order of the voices in the CMN-MEI file. \nExample for an Ars Nova 3-voice motet with different mensurations for each voice: --newvoice_nova i i p p --newvoice_nova i p i p --newvoice_nova p i i i") # for now, just 4 values per voice are allowed
    parser.add_argument('--newvoice_antiqua', nargs=2, action='append', choices=['3','2', 'p', 'i'], default=[], help="Use this flag for each new voice (in Ars Antiqua) that you are entering. After the flag, use '2' or '3' to indicate the 'division of the breve' (duple of triple division) and then use 'p' or 'i' to indicate the 'modusminor'. The order in which you enter the mensuration of the voices here should be the same as the order of the voices in the CMN-MEI file. \nExample for an Ars Antiqua 4-voice motet with 3 minor semibreves per breve and imperfect modus: --newvoice_antiqua 3 i --newvoice_antiqua 3 i --newvoice_antiqua 3 i --newvoice_antiqua 3 i") # for now, you have to add each voice
    args = parser.parse_known_args()
    input_doc = documentFromFile(args.piece).getMeiDocument()
    mensuralDoc = MensuralMeiTranslatedDocument(input_doc, separate_staves_per_voice(input_doc), merge_ties(input_doc), args.which_ars, args.newvoice_nova + args.newvoice_antiqua)
    mensuralDoc.toFile(args.piece[:-4]+"_output.mei")


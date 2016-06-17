from pymei import *


# --------- #
# FUNCTIONS #
# --------- #

# This is for ARS NOVA, which is characterized by the presence of MINIMS and the use of PROLATIO

# Note's Shape Part
# Changes the @dur value to represent mensural figures
def change_note_value(notes, rests, modusminor,tempus, prolatio):
    # Notes can be altered
    for note in notes:
        dur = note.getAttribute('dur').value
        # all notes have a @dur attribute, so the value of @dur is well defined
        if dur == "long":
            if modusminor == 3 and note.hasAttribute('artic') and note.getAttribute('artic').value == "stop":
                # the note has been altered
                mens_dur = "brevis"
            else:
                mens_dur = "longa"
        elif dur == "breve":
            if tempus == 3 and note.hasAttribute('artic') and note.getAttribute('artic').value == "stop":
                # the note has been altered
                mens_dur = "semibrevis"
            else:
                mens_dur = "brevis"
        elif dur == "1":
            if prolatio == 3 and note.hasAttribute('artic') and note.getAttribute('artic').value == "stop":
                # the note has been altered
                mens_dur = "minima"
            else:
                mens_dur = "semibrevis"
        elif dur == "2":
            mens_dur = "minima"
        else:
            print("This is Ars Nova, this note " + note + " shouldn't appear, as its value is " + note.getAttribute('dur').value)
        note.getAttribute('dur').setValue(mens_dur)

    # Rests can't be altered
    # Long-rests don't exist, there only is 1, 2 or 3 breve rests.
    for rest in rests:
        dur = rest.getAttribute('dur').value
        # Due to the mRest part of the code, all the rests have a @dur attribute.
        if dur == "breve":
            mens_dur = "brevis"
        elif dur == "1":
            mens_dur = "semibrevis"
        elif dur == "2":
            mens_dur = "minima"
        elif dur == "long":
            ######## Should and will be 2-breve rest: @dur = "2-breve"
            ##### For now a 2-breve rest is modelled as an imperfection:
            mens_dur = "longa"
            rest.addAttribute('num', '3')
            rest.addAttribute('numbase', '2')
        else: 
        ##### The case of the <mRest> that has already been changed to 'longa' (so it goes according to the mensuration -2 or 3 breves long depending if modusminor = 2 or 3-)
            mens_dur = dur
        rest.getAttribute('dur').setValue(mens_dur)


# Note's Actual Duration Part
# Identifies what notes were Imperfected or Altered and indicates that with the @quality, @num and @numbase attributes
def mark_modification_in_note_duration(notes, triplet_of_minims, modusminor, tempus, prolatio):
    # Default values according to mensuration and presence or absence of triplets of minims in the piece
    if triplet_of_minims:
        semibrevis_default_val = 1024
    else:
        # minima_default_val = 512
        semibrevis_default_val = int(prolatio) * 512    
    brevis_default_val = int(tempus) * semibrevis_default_val
    longa_default_val = int(modusminor) * brevis_default_val

    # Check when a note should be imperfected or altered
    # This check only makes sense for notes (as rests can't be imperfected nor altered)
    # and when the mensuration indicates perfection
    for note in notes:
        durges_num = int(note.getAttribute('dur.ges').value[:-1])

        # Check in accordance to prolatio
        if prolatio == 3:
            imperfected_semibrevis_val = int(semibrevis_default_val * 2/3)
            if durges_num == imperfected_semibrevis_val:
                if note.getAttribute('dur').value == "semibrevis":
                    # Imperfection
                    note.addAttribute('quality', 'i')
                    note.addAttribute('num', '3')
                    note.addAttribute('numbase', '2')
                elif note.getAttribute('dur').value == "minima":
                    # Alteration
                    note.addAttribute('quality', 'a')
                    note.addAttribute('num', '2')
                    note.addAttribute('numbase', '3')
                else:
                    print("MISTAKE!!! this note is neither an imperfected semibrevis nor an altered minima: " + note)

        # Check in accordance to tempus
        if tempus == 3:
            imperfected_brevis_val = int(brevis_default_val * 2/3)
            if durges_num == imperfected_brevis_val:
                if note.getAttribute('dur').value == "brevis":
                    # Imperfection
                    note.addAttribute('quality', 'i')
                    note.addAttribute('num', '3')
                    note.addAttribute('numbase', '2')
                elif note.getAttribute('dur').value == "semibrevis":
                    # Alteration
                    note.addAttribute('quality', 'a')
                    note.addAttribute('num', '2')
                    note.addAttribute('numbase', '3')
                else:
                    print("MISTAKE!!! this note is neither an imperfected brevis nor an altered semibrevis " + note)

        # Check in accordance to modusminor
        if modusminor == 3:
            imperfected_longa_val = int(longa_default_val * 2/3)
            if durges_num == imperfected_longa_val:
                if note.getAttribute('dur').value == "longa":
                    # Imperfection
                    note.addAttribute('quality', 'i')
                    note.addAttribute('num', '3')
                    note.addAttribute('numbase', '2')
                elif note.getAttribute('dur').value == "brevis":
                    # Alteration
                    note.addAttribute('quality', 'a')
                    note.addAttribute('num', '1')
                    note.addAttribute('numbase', '2')
                else:
                    print("MISTAKE!!! this note is neither an imperfected longa nor an altered brevis " + note)    


# ----------- #
# MAIN SCRIPT #
# ----------- #

path = raw_input("Input the path to the MEI file you want to transform into mensural-mei: ")

# Input file part - Separates individual voice information for the parser part
input_doc = documentFromFile(path).getMeiDocument()
staffDef_list = input_doc.getElementsByName('staffDef')
num_voices = len(staffDef_list)
all_voices = []
for i in range(0, num_voices):
    measures_list = input_doc.getElementsByName('measure')
    ind_voice = []
    for measure in measures_list:
        staves_in_measure = measure.getChildrenByName('staff')
        staff = staves_in_measure[i]
        ind_voice.append(staff)
    all_voices.append(ind_voice)

# Ties part
# Join into one the notes that are tied together and give it the right note shape and dur.ges values
ids_removeList = []
ties_list = input_doc.getElementsByName('tie')
for i in range (len(ties_list)-1, -1, -1):
    tie = ties_list[i]
    
    startid = tie.getAttribute('startid').value
    note_startid = startid[1:]  # Removing the '#' character from the startid value, to have the id of the note
    #print(startid)
    #print(note_startid)
    start_note = input_doc.getElementById(note_startid)
    #print(start_note)
    start_dur = start_note.getAttribute('dur').value    # Value of the form: 'long', 'breve', '1' or '2'
    start_durGes = start_note.getAttribute('dur.ges').value    # Value of the form: '1024p'
    start_durGes_number = int(start_durGes[0:len(start_durGes)-1])  # Value of the form: 1024

    endid = tie.getAttribute('endid').value
    note_endid = endid[1:]
    #print(endid)
    #print(note_endid)
    end_note = input_doc.getElementById(note_endid)
    #print(end_note)
    end_dur = end_note.getAttribute('dur').value
    end_durGes = end_note.getAttribute('dur.ges').value
    end_durGes_number = int(end_durGes[0:len(end_durGes)-1])

    if start_durGes == end_durGes:
    # Upgrade the start_note to the next high value figure (two breves --> upgrade to a longa)
    # Remove the second figure
    # Also update the value of the first note (dur.ges)
        
        # dur
        if start_dur == 'breve':    # Other options???
            start_note.getAttribute('dur').setValue('long')
        elif start_dur == '1':
            start_note.getAttribute('dur').setValue('breve')
        else:
            #etc. (what should the etc. consider? are these all the cases?)
            pass
        
        # dur.ges
        start_durGes_number = start_durGes_number + end_durGes_number
        start_durGes = str(start_durGes_number) + "p"
        start_note.getAttribute('dur.ges').setValue(start_durGes)
        ids_removeList.append(end_note.id)

    elif start_durGes_number == end_durGes_number/2 or end_durGes_number == start_durGes_number/2:
    # Take the larger figure [long followed by a breve (or viceversa) --> long] and assign it to the start_note preserves its value
    # Remove then the second figure
    # Also update the value of the first note (dur.ges)

        # dur
        if (start_dur == 'breve' and end_dur == 'long') or (start_dur == 'long' and end_dur == 'breve'):
            start_note.getAttribute('dur').setValue('long')
        elif (start_dur == '1' and end_dur == 'breve') or (start_dur == 'breve' and end_dur == '1'):
            start_note.getAttribute('dur').setValue('breve')
        else:
            # etc. (what should the etc. consider? are these all the cases to take into account?)
            pass

        # durges
        durGes_number = start_durGes_number + end_durGes_number
        durGes = str(durGes_number) + "p"
        start_note.getAttribute('dur.ges').setValue(durGes)
        ids_removeList.append(end_note.id)
    
    else:
        # Again, should I consider another one? Here, I don't think so.
        pass

#print(ids_removeList)

# Output File - Parser Part
output_doc = MeiDocument()
output_doc.root = input_doc.getRootElement()

# ScoreDef Part of the <score> element
# New scoreDef element with the same id as the one in the input file and with the staffGrp element that contains all the staves of the input file
out_scoreDef = MeiElement('scoreDef')
out_scoreDef.id = input_doc.getElementsByName('scoreDef')[0].id

out_staffGrp = input_doc.getElementsByName('staffGrp')[-1]   # This is the one that contains the staves
stavesDef = out_staffGrp.getChildren()
# Mensuration added to the staves
for staffDef in stavesDef:
    voice = staffDef.getAttribute('label').value
    print("Give the mensuration for the " + voice + ":")
    modusminor = raw_input("Modus minor (3 or 2): ")
    tempus = raw_input("Tempus (3 or 2): ")
    prolatio = raw_input("Prolatio (3 or 2): ")
    staffDef.addAttribute('modusminor', modusminor)
    staffDef.addAttribute('tempus', tempus)
    staffDef.addAttribute('prolatio', prolatio)
out_scoreDef.addChild(out_staffGrp)

# Section Part of the <score> element
out_section = MeiElement('section')
out_section.id = input_doc.getElementsByName('section')[0].id

# Add the new <scoreDef> and empty <section> elements to the <score> element after cleaning it up
score = output_doc.getElementsByName('score')[0]
score.deleteAllChildren()
score.addChild(out_scoreDef)
score.addChild(out_section)

# Filling the section element
for ind_voice in all_voices:
    staff = MeiElement('staff')
    out_section.addChild(staff)
    layer = MeiElement('layer')
    staff.addChild(layer)
    for i in range(0, len(ind_voice)):
        musical_content = ind_voice[i].getChildrenByName('layer')[0].getChildren()
        print(ind_voice[i])
        # Adds the elements of each measure into the one voice staff and a barline after each measure content is added
        for element in musical_content:
            # Tied notes
            # If the element is a tied note (other than the first note of the tie), it is not included in the output file (as only the first tied note will be included with the right note shape and duration -@dur.ges-)
            if element.id in ids_removeList:
                print("OUT!")
                pass
            # Tuplets
            elif element.name == 'tuplet':
                print(element)
                tuplet = element
                num = int(tuplet.getAttribute('num').value)
                numbase = int(tuplet.getAttribute('numbase').value)
                notes_grouped = tuplet.getChildren()
                # At the moment we have only found tuplets of "semibrevis" and tuplets of "minima"
                for note in notes_grouped:
                    durges = note.getAttribute('dur.ges').value
                    actual_durges_num = int( int(durges[0:len(durges)-1]) * numbase / num )
                    actual_durges = str(actual_durges_num) + 'p'
                    note.getAttribute('dur.ges').setValue(actual_durges)
                    layer.addChild(note)
            # mRests
            elif element.name == 'mRest':
                rest = MeiElement('rest')
                rest.id = element.id
                rest.setAttributes(element.getAttributes())
                layer.addChild(rest)
                # If there is no duration encoded in the rest, this mRest has the duration of the measure (which, generally, is a long)
                if rest.hasAttribute('dur') == False:
                    ###### All the pieces are bared by the long
                    ####### So when the modusminor = 3, this is a 3-breve rest
                    ####### And when the modusminor = 2, this is a 2-breve rest
                    ###### Its value goes according to the mensuration then.
                    ### FOR NOW: it is changed to a longa right away (so its value will be according to the mensuration)
                    ### And the other long-rests that are note mRests, have to be 2-breve rests in modusminor = 3 
                    ### so they are FOR NOW imperfected in order to make them 2-breve rests
                    ####### THIS SHOULD EVENTUALLY BE CORRECTED WHEN THE MENSURAL-MEI MODULE HAS A WAY TO ENCODE 2-BREVE AND 3-BREVE RESTS\
                    rest.addAttribute('dur', 'longa')
            # Notes and simple rests
            else:
                print(element)
                layer.addChild(element)
        print("BARLINE - BARLINE - BARLINE")
        layer.addChild(MeiElement('barLine'))


# Notice the presence (or absence) of triplets of minims in the piece:

#Obtain all the dur.ges of the notes in the score
notes = output_doc.getElementsByName('note')
durges_list = []
for note in notes:
    durges = note.getAttribute('dur.ges').value
    if durges not in durges_list:
        durges_list.append(durges)
# Sets the triplet_of_minims flag to True or False
triplet_of_minims = False
if '341p' in durges_list:
    triplet_of_minims = True

# Modify the note shape (@dur) and sets the note quality (imperfect/altered) to encode its mensural value. 
# This is done for the notes of each voice, taking into account the mensuration of each voice.
staffDefs = output_doc.getElementsByName('staffDef')
staves = output_doc.getElementsByName('staff')
for i in range(0, len(staffDefs)):
    staffDef = staffDefs[i]
    modusminor = int(staffDef.getAttribute('modusminor').value)
    tempus = int(staffDef.getAttribute('tempus').value)
    prolatio = int(staffDef.getAttribute('prolatio').value)
    notes_per_voice = staves[i].getChildrenByName('layer')[0].getChildrenByName('note')
    rests_per_voice = staves[i].getChildrenByName('layer')[0].getChildrenByName('rest')
    change_note_value(notes_per_voice, rests_per_voice, modusminor, tempus, prolatio)
    mark_modification_in_note_duration(notes_per_voice, triplet_of_minims, modusminor, tempus, prolatio)

# Removing or replacing extraneous attributes on the notes
notes = output_doc.getElementsByName('note')
for note in notes:
    # Removing extraneous attributes in the <note> element
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
    # Replacement of extraneous attributes by appropriate mensural attributes or elements within the <note> element:
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
            note.addChild(MeiElement('dot'))
            note.removeAttribute('artic')
        elif artic.value == "ten":
            note.addAttribute('stem.dir', 'down') # If the note has this attribute (@stem.dir) already, it overwrites its value
            note.removeAttribute('artic')

outputfile = path[0:len(path)-4] + "_output.mei"
documentToFile(output_doc, outputfile)

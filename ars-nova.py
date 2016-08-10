from pymei import *
from fractions import *


# --------- #
# FUNCTIONS #
# --------- #

# This is for ARS NOVA, which is characterized by the presence of MINIMS and the use of PROLATIO

# Identifies the relative values of the notes (its performed values) according to the mensuration
def relative_vals(triplet_of_minims, modusmaior, modusminor, tempus, prolatio):
    if triplet_of_minims:
        semibrevis_default_val = 1024
    else:
        # minima_default_val = 512
        semibrevis_default_val = prolatio * 512
    brevis_default_val = tempus * semibrevis_default_val
    longa_default_val = modusminor * brevis_default_val
    maxima_default_val = modusmaior * longa_default_val

    return [semibrevis_default_val, brevis_default_val, longa_default_val, maxima_default_val]

# Returns the imperfect and perfect values of the notes
def imp_perf_vals(triplet_of_minims_flag, modusmaior, modusminor, tempus, prolatio):
    semibrevis_default_val, brevis_default_val, longa_default_val, maxima_default_val = relative_vals(triplet_of_minims_flag, modusmaior, modusminor, tempus, prolatio)
    if prolatio == 2:
        semibrevis_imp = semibrevis_default_val
        semibrevis_perf = int(1.5 * semibrevis_default_val)
    elif prolatio == 3:
        semibrevis_imp = int(semibrevis_default_val * 2/3)
        semibrevis_perf = semibrevis_default_val
    else:
        pass
    brevis_imp = semibrevis_default_val * 2
    brevis_perf = semibrevis_default_val * 3
    longa_imp = brevis_default_val * 2
    longa_perf = brevis_default_val * 3
    maxima_imp = longa_default_val * 2
    maxima_perf = longa_default_val * 3
    return [[semibrevis_default_val, semibrevis_imp, semibrevis_perf], [brevis_default_val, brevis_imp, brevis_perf], [longa_default_val, longa_imp, longa_perf], [maxima_default_val, maxima_imp, maxima_perf]]

# Performs the actual change, in notes and rests, from contemporary to mensural notation. This involves 2 steps:
# 1. Note/Rest Shape part: Changes the @dur value to represent mensural figures
# 2. Note's Actual Duration part: Identifies which notes were 'perfected', 'imperfected' or 'altered' and indicates this with the attributes: @quality, @num and @numbase
def noterest_to_mensural(notes, rests, modusmaior, modusminor, tempus, prolatio, triplet_of_minims_flag):
    list_values = imp_perf_vals(triplet_of_minims_flag, modusmaior, modusminor, tempus, prolatio)
    sb_def, sb_imp, sb_perf = list_values[0]
    b_def, b_imp, b_perf = list_values[1]
    l_def, l_imp, l_perf = list_values[2]
    max_def, max_imp, max_perf = list_values[3]

    # Note's Part:
    for note in notes:
        dur = note.getAttribute('dur').value
        durges_num = int(note.getAttribute('dur.ges').value[:-1])

        # For the tied notes:
        # First find its right (contemporary) duration
        if dur == 'TiedNote!':
            # Maximas
            if (int(max_imp * 5/6) - 1) <= durges_num and durges_num <= max_perf:
                dur = 'maxima'
            # Longas
            elif (int(l_imp * 5/6) - 1) <= durges_num and durges_num <= l_perf:
                dur = 'long'
            # Breves
            elif (int(b_imp * 5/6) - 1) <= durges_num and durges_num <= b_perf:
                dur = 'breve'
            # Semibreves
            elif (int(sb_imp * 5/6) - 1) <= durges_num and durges_num <= sb_perf:
                dur = '1'
            else:
                print("Weird\n The tied note doesn't seem to be any note (perfect, imperfect, or afected by patial imperfection) in the range of semibreve to maxima - " + str(note) + ", its duration is " + str(durges_num) + "p")
            note.getAttribute('dur').setValue(dur)

        # Look for the corresponding mensural duration of the notes

        # MAXIMA
        if dur == 'maxima':
            # Default @dur value of the note (Exception: Altered Longa)
            mens_dur = 'maxima'

            # Looking for 'perfections', 'imperfections' (including partial imperfection) and 'alterations'
            if durges_num == max_perf:
                # Perfection case
                if modusmaior == 2:
                    note.addAttribute('quality', 'p')
                    note.addAttribute('num', '2')
                    note.addAttribute('numbase', '3')
                    # # And we add a dot of perfection
                    # if not note.hasChildren('dot'):
                    #     dot = MeiElement('dot')
                    #     note.addChild('dot')
                    # dot = note.getChildrenByName('dot')
                    # dot.addAttribute('format', 'aug')
                # Default case
                elif modusmaior == 3:
                    pass
                # Mensuration MISTAKE: 'modusmaior'
                else:
                    print("MISTAKE IN MENSURATION: modusmaior")
                    pass
            elif durges_num == max_imp:
                if modusmaior == 3:
                    # Alteration case - here the @dur attribute changes
                    if note.hasAttribute('artic') and note.getAttribute('artic').value == 'stop':
                        mens_dur = 'longa'
                        note.addAttribute('quality', 'a')
                        note.addAttribute('num', '1')
                        note.addAttribute('numbase', '2')
                    # Imperfection case
                    else:
                        note.addAttribute('quality', 'i')
                        note.addAttribute('num', '3')
                        note.addAttribute('numbase', '2')
                # Default case
                elif modusmaior == 2:
                    pass
                # Mensuration MISTAKE: 'modusmaior'
                else:
                    print("MISTAKE IN MENSURATION: modusmaior")
                    pass
            else:
            # Check for partial imperfection (and for mistakes)
                ratio = Fraction(durges_num, max_def)
                # Immediate imperfection: modusminor should be 3
                if modusminor == 3 and modusmaior == 2 and ratio == Fraction(5,6):
                    note.addAttribute('quality', 'immediate imperfection')
                    note.addAttribute('num', str(ratio.denominator))
                    note.addAttribute('numbase', str(ratio.numerator))
                elif modusminor == 3 and modusmaior == 3 and ratio == Fraction(5,9):
                    note.addAttribute('quality', 'immediate imperfection (2)')
                    note.addAttribute('num', str(ratio.denominator))
                    note.addAttribute('numbase', str(ratio.numerator))
                elif modusminor == 3 and modusmaior == 3 and ratio == Fraction(8,9):
                    note.addAttribute('quality', 'immediate imperfection')
                    note.addAttribute('num', str(ratio.denominator))
                    note.addAttribute('numbase', str(ratio.numerator))
                # Remote imperfection: tempus should be 3
                elif tempus == 3 and modusminor == 2 and modusmaior == 2 and ratio == Fraction(11,12):
                    note.addAttribute('quality', 'remote imperfection')
                    note.addAttribute('num', str(ratio.denominator))
                    note.addAttribute('numbase', str(ratio.numerator))
                elif tempus == 3 and modusminor == 2 and modusmaior == 3 and ratio == Fraction(11,18):
                    note.addAttribute('quality', 'remote imperfection (2)')
                    note.addAttribute('num', str(ratio.denominator))
                    note.addAttribute('numbase', str(ratio.numerator))
                elif tempus == 3 and modusminor == 2 and modusmaior == 3 and ratio == Fraction(17,18):
                    note.addAttribute('quality', 'remote imperfection')
                    note.addAttribute('num', str(ratio.denominator))
                    note.addAttribute('numbase', str(ratio.numerator))
                elif tempus == 3 and modusminor == 3 and modusmaior == 2 and ratio == Fraction(17,18):
                    note.addAttribute('quality', 'remote imperfection')
                    note.addAttribute('num', str(ratio.denominator))
                    note.addAttribute('numbase', str(ratio.numerator))
                elif tempus == 3 and modusminor == 3 and modusmaior == 3 and ratio == Fraction(17,27):
                    note.addAttribute('quality', 'remote imperfection (2)')
                    note.addAttribute('num', str(ratio.denominator))
                    note.addAttribute('numbase', str(ratio.numerator))
                elif tempus == 3 and modusminor == 3 and modusmaior == 3 and ratio == Fraction(26,27):
                    note.addAttribute('quality', 'remote imperfection')
                    note.addAttribute('num', str(ratio.denominator))
                    note.addAttribute('numbase', str(ratio.numerator))
                # Note's value MISTAKE
                else:
                    print("This MAXIMA " + str(note) + " has an inappropriate duration @dur.ges = " + str(durges_num) + "p, as it is " + str(ratio.numerator) + "/" + str(ratio.denominator) + " part of its normal value.")
                    pass

        # LONGA
        elif dur == 'long':
            # Default @dur value of the note (Exception: Altered Breve)
            mens_dur = 'longa'

            # Looking for 'perfections', 'imperfections' (including partial imperfection) and 'alterations'
            if durges_num == l_perf:
                # Perfection case
                if modusminor == 2:
                    note.addAttribute('quality', 'p')
                    note.addAttribute('num', '2')
                    note.addAttribute('numbase', '3')
                    # # And we add a dot of perfection
                    # if not note.hasChildren('dot'):
                    #     dot = MeiElement('dot')
                    #     note.addChild('dot')
                    # dot = note.getChildrenByName('dot')
                    # dot.addAttribute('format', 'aug')
                # Default case
                elif modusminor == 3:
                    pass
                # Mensuration MISTAKE: 'modusminor'
                else:
                    print("MISTAKE IN MENSURATION: modusminor")
                    pass
            elif durges_num == l_imp:
                if modusminor == 3:
                    # Alteration case - here the @dur attribute changes
                    if note.hasAttribute('artic') and note.getAttribute('artic').value == 'stop':
                        mens_dur = 'brevis'
                        note.addAttribute('quality', 'a')
                        note.addAttribute('num', '1')
                        note.addAttribute('numbase', '2')
                    # Imperfection case
                    else:
                        note.addAttribute('quality', 'i')
                        note.addAttribute('num', '3')
                        note.addAttribute('numbase', '2')
                # Default case
                elif modusminor == 2:
                    pass
                # Mensuration MISTAKE: 'modusminor'
                else:
                    print("MISTAKE IN MENSURATION: modusminor")
                    pass
            else:
            # Check for partial imperfection (and for mistakes)
                ratio = Fraction(durges_num, l_def)
                # Immediate imperfection: tempus should be 3
                if tempus == 3 and modusminor == 2 and ratio == Fraction(5,6):
                    note.addAttribute('quality', 'immediate imperfection')
                    note.addAttribute('num', str(ratio.denominator))
                    note.addAttribute('numbase', str(ratio.numerator))
                elif tempus == 3 and modusminor == 3 and ratio == Fraction(5,9):
                    note.addAttribute('quality', 'immediate imperfection (2)')
                    note.addAttribute('num', str(ratio.denominator))
                    note.addAttribute('numbase', str(ratio.numerator))
                elif tempus == 3 and modusminor == 3 and ratio == Fraction(8,9):
                    note.addAttribute('quality', 'immediate imperfection')
                    note.addAttribute('num', str(ratio.denominator))
                    note.addAttribute('numbase', str(ratio.numerator))
                # Remote imperfection: prolatio should be 3
                elif prolatio == 3 and tempus == 2 and modusminor == 2 and ratio == Fraction(11,12):
                    note.addAttribute('quality', 'remote imperfection')
                    note.addAttribute('num', str(ratio.denominator))
                    note.addAttribute('numbase', str(ratio.numerator))
                elif prolatio == 3 and tempus == 2 and modusminor == 3 and ratio == Fraction(11,18):
                    note.addAttribute('quality', 'remote imperfection (2)')
                    note.addAttribute('num', str(ratio.denominator))
                    note.addAttribute('numbase', str(ratio.numerator))
                elif prolatio == 3 and tempus == 2 and modusminor == 3 and ratio == Fraction(17,18):
                    note.addAttribute('quality', 'remote imperfection')
                    note.addAttribute('num', str(ratio.denominator))
                    note.addAttribute('numbase', str(ratio.numerator))
                elif prolatio == 3 and tempus == 3 and modusminor == 2 and ratio == Fraction(17,18):
                    note.addAttribute('quality', 'remote imperfection')
                    note.addAttribute('num', str(ratio.denominator))
                    note.addAttribute('numbase', str(ratio.numerator))
                elif prolatio == 3 and tempus == 3 and modusminor == 3 and ratio == Fraction(17,27):
                    note.addAttribute('quality', 'remote imperfection (2)')
                    note.addAttribute('num', str(ratio.denominator))
                    note.addAttribute('numbase', str(ratio.numerator))
                elif prolatio == 3 and tempus == 3 and modusminor == 3 and ratio == Fraction(26,27):
                    note.addAttribute('quality', 'remote imperfection')
                    note.addAttribute('num', str(ratio.denominator))
                    note.addAttribute('numbase', str(ratio.numerator))
                # Note's value MISTAKE
                else:
                    print("This LONG " + str(note) + " has an inappropriate duration @dur.ges = " + str(durges_num) + "p, as it is " + str(ratio.numerator) + "/" + str(ratio.denominator) + " part of its normal value.")
                    pass

        # BREVIS
        elif dur == 'breve':
            # Default @dur value of the note (Exception: Altered Semibreve)
            mens_dur = 'brevis'

            # Looking for 'perfections', 'imperfections' (including partial imperfection) and 'alterations'
            if durges_num == b_perf:
                # Perfection case
                if tempus == 2:
                    note.addAttribute('quality', 'p')
                    note.addAttribute('num', '2')
                    note.addAttribute('numbase', '3')
                    # # And we add a dot of perfection
                    # if not note.hasChildren('dot'):
                    #     dot = MeiElement('dot')
                    #     note.addChild('dot')
                    # dot = note.getChildrenByName('dot')
                    # dot.addAttribute('format', 'aug')
                # Default case
                elif tempus == 3:
                    pass
                # Mensuration MISTAKE: 'tempus'
                else:
                    print("MISTAKE IN MENSURATION: tempus")
                    pass
            elif durges_num == b_imp:
                if tempus == 3:
                    # Alteration case - here the @dur attribute changes
                    if note.hasAttribute('artic') and note.getAttribute('artic').value == 'stop':
                        mens_dur = 'semibrevis'
                        note.addAttribute('quality', 'a')
                        note.addAttribute('num', '1')
                        note.addAttribute('numbase', '2')
                    # Imperfection case
                    else:
                        note.addAttribute('quality', 'i')
                        note.addAttribute('num', '3')
                        note.addAttribute('numbase', '2')
                # Default case
                elif tempus == 2:
                    pass
                # Mensuration MISTAKE: 'tempus'
                else:
                    print("MISTAKE IN MENSURATION: tempus")
                    pass
            else:
            # Check for partial imperfection (and for mistakes)
                ratio = Fraction(durges_num, b_def)
                # Immediate imperfection: prolatio should be 3
                if prolatio == 3 and tempus == 2 and ratio == Fraction(5,6):
                    note.addAttribute('quality', 'immediate imperfection')
                    note.addAttribute('num', str(ratio.denominator))
                    note.addAttribute('numbase', str(ratio.numerator))
                elif prolatio == 3 and tempus == 3 and ratio == Fraction(5,9):
                    note.addAttribute('quality', 'immediate imperfection (2)')
                    nnote.addAttribute('num', str(ratio.denominator))
                    note.addAttribute('numbase', str(ratio.numerator))
                elif prolatio == 3 and tempus == 3 and ratio == Fraction(8,9):
                    note.addAttribute('quality', 'immediate imperfection')
                    note.addAttribute('num', str(ratio.denominator))
                    note.addAttribute('numbase', str(ratio.numerator))
                # There is no 'Remote imperfection' in case of a 'breve'
                # Note's value MISTAKE
                else:
                    print("This BREVE " + str(note) + " has an inappropriate duration @dur.ges = " + str(durges_num) + "p, as it is " + str(ratio.numerator) + "/" + str(ratio.denominator) + " part of its normal value.")
                    pass

        # SEMIBREVIS
        elif dur == '1':
            # Default @dur value of the note (Exception: Altered Minim)
            mens_dur = 'semibrevis'

            # Looking for 'perfections', 'imperfections' (including partial imperfection) and 'alterations'
            if durges_num == sb_perf:
                # Perfection case
                if prolatio == 2:
                    note.addAttribute('quality', 'p')
                    note.addAttribute('num', '2')
                    note.addAttribute('numbase', '3')
                    # # And we add a dot of perfection
                    # if not note.hasChildren('dot'):
                    #     dot = MeiElement('dot')
                    #     note.addChild('dot')
                    # dot = note.getChildrenByName('dot')
                    # dot.addAttribute('format', 'aug')
                # Default case
                elif prolatio == 3:
                    pass
                # Mensuration MISTAKE: 'prolatio'
                else:
                    print("MISTAKE IN MENSURATION: prolatio")
                    pass
            elif durges_num == sb_imp:
                if prolatio == 3:
                    # Alteration case - here the @dur attribute changes
                    if note.hasAttribute('artic') and note.getAttribute('artic').value == 'stop':
                        mens_dur = 'minima'
                        note.addAttribute('quality', 'a')
                        note.addAttribute('num', '1')
                        note.addAttribute('numbase', '2')
                    # Imperfection case
                    else:
                        note.addAttribute('quality', 'i')
                        note.addAttribute('num', '3')
                        note.addAttribute('numbase', '2')
                # Default case
                elif prolatio == 2:
                    pass
                # Mensuration MISTAKE: 'prolatio'
                else:
                    print("MISTAKE IN MENSURATION: prolatio")
                    pass
            else:
            # Check for mistakes (there is no partial imperfection for a semibreve)
                # Note's value MISTAKE
                print("This SEMIBREVE " + str(note) + " has an inappropriate duration @dur.ges = " + str(durges_num) + "p, as it is " + str(Fraction(durges_num, sb_def).numerator) + "/" + str(Fraction(durges_num, sb_def).denominator) + " part of its normal value.")
                pass

        # MINIMA
        elif dur == '2':
            mens_dur = 'minima'

        # INCORRECT NOTE VALUE
        else:
            if dur != "TiedNote!":
                print("This note shouldn't be here, as it is larger than a maxima or shorter than a minima! " + str(note) + ", " + str(dur) + ", " + str(durges_num) + "p")
                mens_dur = dur
            else:
                print("Still tied-note")

        # Change the @dur value to the corresponding mensural note value
        note.getAttribute('dur').setValue(mens_dur)


    # Rest's Part:
    for rest in rests:
        # Due to the mRest part of the code, all the rests have a @dur attribute.
        dur = rest.getAttribute('dur').value
        # Minim rest
        if dur == "2":
            mens_dur = "minima"
        # Semibreve rest
        elif dur == "1":
            mens_dur = "semibrevis"
            # Check for mistakes in duration (@dur.ges attribute)
            if rest.hasAttribute('dur.ges'):
                durges_num = int(rest.getAttribute('dur.ges').value[:-1]) 
                if durges_num != sb_def:
                    print("This SEMIBREVE rest " + str(rest) + ", doesn't have the appropriate @dur.ges value, as it is " + str(durges_num) + "p, instead of " + str(sb_def) + "p;")
                    print("i.e., instead of being " + str(prolatio) + " times a MINIM, it is " + str(float(durges_num * prolatio)/ sb_def) + " times a MINIM")
                    print("SO IT IS: " + str(Fraction(durges_num, sb_def).numerator) + "/" + str(Fraction(durges_num, sb_def).denominator) + " ITS DEFAULT VALUE\n")
        # Breve rest
        elif dur == "breve":
            mens_dur = "brevis" # 1B rest??????????
            # Check for mistakes in duration (@dur.ges attribute)
            if rest.hasAttribute('dur.ges'):
                durges_num = int(rest.getAttribute('dur.ges').value[:-1])
                if durges_num != b_def:
                    print("This BREVE rest " + str(rest) + ", doesn't have the appropriate @dur.ges value, as it is " + str(durges_num) + "p, instead of " + str(b_def) + "p;")
                    print("i.e., instead of being " + str(tempus) + " times a SEMIBREVE, it is " + str(float(durges_num * tempus)/ b_def) + " times a SEMIBREVE")
                    print("SO IT IS: " + str(Fraction(durges_num, b_def).numerator) + "/" + str(Fraction(durges_num, b_def).denominator) + " ITS DEFAULT VALUE\n")
        # 2-breve and 3-breve rest
        elif dur == "long":
            ##########################################################################################################
            mens_dur = "longa" # THIS WONT BE HERE, INSTEAD WE WILL USE THE MENS_DUR SPECIFIED IN EACH CONDITION (IF)
            ##########################################################################################################
            if rest.hasAttribute('dur.ges'):
                durges_num = int(rest.getAttribute('dur.ges').value[:-1])
                # 2-breve rest
                if durges_num == l_imp:
                    rest.addAttribute('EVENTUALDUR', '2B')  # It will be:   mens_dur = '2B'
                    ###################################################################################################################
                    ###### This will go away when the 3B and 2B rests (3-spaces and 2-spaces rests) are implemented in Verovio ########
                    if modusminor == 3: # 'imperfected'
                        rest.addAttribute('num', '3')
                        rest.addAttribute('numbase', '2')
                    else:   # Default
                        pass
                    ###################################################################################################################
                # 3-breve rest
                elif durges_num == l_perf:
                    rest.addAttribute('EVENTUALDUR', '3B')  # It will be:   mens_dur = '3B'
                    ###################################################################################################################
                    ###### This will go away when the 3B and 2B rests (3-spaces and 2-spaces rests) are implemented in Verovio ########
                    if modusminor == 2: # 'perfected'
                        rest.addAttribute('num', '2')
                        rest.addAttribute('numbase', '3')
                    else:   # Default
                        pass
                    ###################################################################################################################
                # Check for mistakes in duration (@dur.ges attribute)
                else:
                    print("This 'LONG' Rest " + str(rest) + ", doesn't have the appropriate @dur.ges value, as it is " + str(durges_num) + "p, instead of " + str(l_imp) + "p or " + str(l_perf) + "p")
                    print("i.e., it isn't a 2-breve or 3-breve rest, instead it is: " +  str(Fraction(durges_num, b_def).numerator) + "/" + str(Fraction(durges_num, b_def).denominator) + " times a BREVE rest\n")
            else:
                # 3-breve rest
                if modusminor == 3:
                    rest.addAttribute('EVENTUALDUR', '3B')
                #2-breve rest
                elif modusminor == 2:
                    rest.addAttribute('EVENTUALDUR', '2B')
                # Check for mistakes in duration (@dur.ges attribute)
                else:
                    print("This 'LONG' Rest " + str(rest) + ", doesn't have the appropriate @dur.ges value")
        # Mistake in rest's duration (@dur attribute)
        else:
            print("This kind of Rest shouldn't be in this repertory " + str(note) + ", it has a duration of  " + str(dur) + "\n")
            mens_dur = dur

        # Change the @dur value to the corresponding mensural note value
        rest.getAttribute('dur').setValue(mens_dur)


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
# Join into one the notes that are tied together:
# 1. Sets the @dur of the first note of the tied notes to the value 'TiedNote!'
# 2. And its @dur.ges to the result of the sum of the performance duration (@dur.ges) of the individual notes that make up the tie
# Store a list of the other notes that make up the tie (the ones after the first) to remove them from the output document
ids_removeList = []
ties_list = input_doc.getElementsByName('tie')
for i in range (len(ties_list)-1, -1, -1):
    tie = ties_list[i]
    
    # Start note
    startid = tie.getAttribute('startid').value
    note_startid = startid[1:]  # Removing the '#' character from the startid value, to have the id of the note
    start_note = input_doc.getElementById(note_startid)
    start_dur = start_note.getAttribute('dur').value    # Value of the form: 'long', 'breve', '1' or '2'
    start_durGes_number = int(start_note.getAttribute('dur.ges').value[:-1])    # Value of the form: 1024

    # End note
    endid = tie.getAttribute('endid').value
    note_endid = endid[1:]
    end_note = input_doc.getElementById(note_endid)
    end_dur = end_note.getAttribute('dur').value
    end_durGes_number = int(end_note.getAttribute('dur.ges').value[:-1])

    # Calculation of the @dur.ges
    durGes_number = start_durGes_number + end_durGes_number
    durGes = str(durGes_number) + "p"
    start_note.getAttribute('dur.ges').setValue(durGes)
    ids_removeList.append(end_note.id)

    # Sets @dur = 'TiedNote!'
    start_note.getAttribute('dur').setValue('TiedNote!')
#print(ids_removeList)


# Output File - Parser Part
output_doc = MeiDocument()
output_doc.root = input_doc.getRootElement()

# ScoreDef Part of the <score> element:
out_scoreDef = MeiElement('scoreDef')
# Make it share the id (@xml:id) it has in the input file
out_scoreDef.id = input_doc.getElementsByName('scoreDef')[0].id
# Add as its child the <staffGrp> element, with all the <staffDef> elements and the right mensuration (@modusmaior, @modusminor, @tempus and @prolatio) for each one
out_staffGrp = input_doc.getElementsByName('staffGrp')[-1]
# The [-1] guarantees that the <staffGrp> element taken is the one which contains the <staffDef> elements (previous versions of the plugin stored a <staffGrp> element inside another <staffGrp>)
stavesDef = out_staffGrp.getChildren()
# Mensuration added to the staves definition <staffDef>
for staffDef in stavesDef:
    voice = staffDef.getAttribute('label').value
    print("Give the mensuration for the " + voice + ":")
    modusminor = raw_input("Modus minor (3 or 2): ")
    tempus = raw_input("Tempus (3 or 2): ")
    prolatio = raw_input("Prolatio (3 or 2): ")
    staffDef.addAttribute('modusmaior', '2')
    staffDef.addAttribute('modusminor', modusminor)
    staffDef.addAttribute('tempus', tempus)
    staffDef.addAttribute('prolatio', prolatio)
out_scoreDef.addChild(out_staffGrp)

# Section Part of the <score> element:
out_section = MeiElement('section')
out_section.id = input_doc.getElementsByName('section')[0].id

# Add the new <scoreDef> and empty <section> elements to the <score> element after cleaning it up
score = output_doc.getElementsByName('score')[0]
score.deleteAllChildren()
score.addChild(out_scoreDef)
score.addChild(out_section)

# Filling the section element:
for ind_voice in all_voices:
    # Add a staff for each voice, with the id corresponding to the first <staff> element in the input_file for that exact voice
    staff = MeiElement('staff')
    staff.setId(input_doc.getElementsByName('staff')[all_voices.index(ind_voice)].id)
    out_section.addChild(staff)
    # Add a layer inside the <staff> for each voice, with the id corresponding to the first <layer> element in the input_file for that exact voice
    layer = MeiElement('layer')
    layer.setId(input_doc.getElementsByName('layer')[all_voices.index(ind_voice)].id)
    staff.addChild(layer)
    # Fill each voice (fill the <layer> of each <staff>) with musical information (notes/rests)
    for i in range(0, len(ind_voice)):
        musical_content = ind_voice[i].getChildrenByName('layer')[0].getChildren()
        # Add the elements of each measure into the <layer> and a <barLine/> element after the measure-content
        for element in musical_content:
            # Tied notes
            # If the element is a tied note (other than the first note of the tie: <note @dur = 'TiedNote!'/>), it is not included in the output file (as only the first tied note will be included with the right note shape and duration -@dur.ges-)
            if element.id in ids_removeList:
                pass
            # Tuplets
            elif element.name == 'tuplet':
                tuplet = element
                num = int(tuplet.getAttribute('num').value)
                numbase = int(tuplet.getAttribute('numbase').value)
                notes_grouped = tuplet.getChildren()
                # The only tuplets present in Ars Nova are tuplets of minims
                for note in notes_grouped:
                    durges = note.getAttribute('dur.ges').value
                    actual_durges_num = int( int(durges[0:len(durges)-1]) * numbase / num )
                    actual_durges = str(actual_durges_num) + 'p'
                    note.getAttribute('dur.ges').setValue(actual_durges)
                    layer.addChild(note)
            # mRests
            elif element.name == 'mRest':
                # Change into simple <rest> elements (as there are no measure-rests in mensural notation)
                rest = MeiElement('rest')
                rest.id = element.id
                rest.setAttributes(element.getAttributes())
                layer.addChild(rest)
                # If there is no duration encoded in the rest, this mRest has the duration of the measure (which, generally, is a long)
                if rest.hasAttribute('dur') == False:
                    rest.addAttribute('dur', 'long')
            # Notes and simple rests
            else:
                layer.addChild(element)
        # Add barline
        layer.addChild(MeiElement('barLine'))


# Establish the presence (or absence) of triplets of minims in the piece:

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

# Modify the note shape (@dur) and sets the note quality (perfect/imperfect/altered) to encode its mensural value. 
# This is done for the notes (and rests, just the @dur part) of each voice, taking into account the mensuration of each voice.
staffDefs = output_doc.getElementsByName('staffDef')
staves = output_doc.getElementsByName('staff')
for i in range(0, len(staffDefs)):
    staffDef = staffDefs[i]
    modusmaior = int(staffDef.getAttribute('modusmaior').value)
    modusminor = int(staffDef.getAttribute('modusminor').value)
    tempus = int(staffDef.getAttribute('tempus').value)
    prolatio = int(staffDef.getAttribute('prolatio').value)
    
    notes_per_voice = staves[i].getChildrenByName('layer')[0].getChildrenByName('note')
    rests_per_voice = staves[i].getChildrenByName('layer')[0].getChildrenByName('rest')

    print("\n" + str(staffDef.getAttribute('label').value).upper())
    print "Sb       B     L     Max"
    print(relative_vals(triplet_of_minims, modusmaior, modusminor, tempus, prolatio))
    print ""
    noterest_to_mensural(notes_per_voice, rests_per_voice, modusmaior, modusminor, tempus, prolatio, triplet_of_minims)

# Remove/Replace extraneous attributes on the notes
notes = output_doc.getElementsByName('note')
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
    # Replace extraneous attributes by the appropriate mensural attributes or elements within the <note> element:
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

# Removing @dots from <rest> elements
rests = output_doc.getElementsByName('rest')
for rest in rests:
    if rest.hasAttribute('dots'):
        rest.removeAttribute('dots')

outputfile = path[0:len(path)-4] + "_output.mei"
documentToFile(output_doc, outputfile)

"""
white_notation module

Contains all the relevant functions for translating White Mensural Notation pieces written in CMN-MEI to Mensural-MEI

Functions:
relative_vals -- Return a list of the default performed duration of the different notes
imp_perf_vals -- Return a list of the default / imperfect / perfect performed duration of the different notes
partial_imperfection -- Identify when a note experimented a partial imperfection and return True/False
noterest_to_mensural -- Perform the actual change, in notes and rests, from contemporary to mensural notation
fill_section -- Fill the output <section> element with the appropriate musical content
"""
# White mensural notation is essentially the same as the black notation from the Ars Nova.
# The only difference is that it includes shorter note values (i.e., semiminim, fusa, and semifusa),
# and the barring is generally done at the level of the breve (instead of the long).
from fractions import *

from pymei import *


def relative_vals(triplet_of_minims, modusmaior, modusminor, tempus, prolatio):
    """
    Return a list of the (default) performed duration of the notes on one voice according to the mensuration of the voice and the presence/absence of triplet of minims.

    Arguments:
    modusmaior, modusminor, tempus, prolatio -- integer values (3 or 2) that give the mensuration of the voice
    triplet_of_minims -- boolean flag that indicates the presence of a 'triplet of minims' in the piece (all voices)

    Return value:
    List of the default performed duration of the notes in the following order: semibreve, breve, long and maxima.
    """
    if triplet_of_minims:
        semibrevis_default_val = 1024
    else:
        # minima_default_val = 512
        semibrevis_default_val = prolatio * 512
    brevis_default_val = tempus * semibrevis_default_val
    longa_default_val = modusminor * brevis_default_val
    maxima_default_val = modusmaior * longa_default_val

    return [semibrevis_default_val, brevis_default_val, longa_default_val, maxima_default_val]


def imp_perf_vals(triplet_of_minims_flag, modusmaior, modusminor, tempus, prolatio):
    """
    Return a list of lists with the performed duration of each note in its different states (default / imperfect / perfect).

    Arguments:
    modusmaior, modusminor, tempus, prolatio -- integer values (3 or 2) that give the mensuration of the voice
    triplet_of_minims -- boolean flag that indicates the presence of a 'triplet of minims' in the piece (all voices)

    Return value:
    List of four, 3-element, sublists. Each sublist belongs to one note type (semibrevis, brevis, longa and maxima), and indicates the performed duration of the particular note in 3 states: default, imperfect and perfect.
    """
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


def partial_imperfection(note, ratio, modusminor, tempus, prolatio = None):
    """Identify when a note experimented a partial imperfection and return True in that case, otherwise return False.

    When a note experimented a partial imperfection, besides returning True, this function adds the appropriate @quality, @num and @numbase attributes.

    Arguments:
    note -- A <note> element in a particular voice on the mei document
    ratio -- The ratio between the actual performed duration of the <note> and its default performed duration
    modusminor, tempus, prolatio -- Integer values (3 or 2) that give the mensuration of the voice. The last argument is optional (default None).
    When the note is a 'longa' these exact arguments are used: modusminor, tempus and prolatio. 
    When the note is a 'maxima', these arguments stand for: modusmaior, modusminor and tempus, respectively.
    When the note is a breve, these arguments stand for: tempus, prolatio and None (the last argument is left blank).
    """
    # From the beginning, we assume there is a partial imperfection.
    # But if none of the 'partial imperfection' conditions are satisfied, the partial_imperf flag would change to False.
    partial_imperf = True

    # Immediate imperfection: tempus should be 3
    if tempus == 3 and modusminor == 2 and ratio == Fraction(5,6):
        note.addAttribute('quality', 'immediate_imp')
    elif tempus == 3 and modusminor == 3 and ratio == Fraction(5,9):
        note.addAttribute('quality', 'imperfection + immediate_imp')
    elif tempus == 3 and modusminor == 3 and ratio == Fraction(8,9):
        note.addAttribute('quality', 'immediate_imp')

    # Remote imperfection: there should be a prolatio value, and it should be 3
    elif prolatio is not None:
        if prolatio == 3 and tempus == 2 and modusminor == 2 and ratio == Fraction(11,12):
            note.addAttribute('quality', 'remote_imp')
        elif prolatio == 3 and tempus == 2 and modusminor == 3 and ratio == Fraction(11,18):
            note.addAttribute('quality', 'imperfection + remote_imp')
        elif prolatio == 3 and tempus == 2 and modusminor == 3 and ratio == Fraction(17,18):
            note.addAttribute('quality', 'remote_imp')
        elif prolatio == 3 and tempus == 3 and modusminor == 2 and ratio == Fraction(17,18):
            note.addAttribute('quality', 'remote_imp')
        elif prolatio == 3 and tempus == 3 and modusminor == 3 and ratio == Fraction(17,27):
            note.addAttribute('quality', 'imperfection + remote_imp')
        elif prolatio == 3 and tempus == 3 and modusminor == 3 and ratio == Fraction(26,27):
            note.addAttribute('quality', 'remote_imp')
        # It is not a 'remote partial imperfection' nor an 'immediate partial imperfection'
        else:
            partial_imperf = False

    # It is not an 'immediate partial imperfection' and there is no possibility of 'remote imperfection' as there is no 'prolatio'
    else:
        partial_imperf = False

    # Add the @num and @numbase attributes in case of partial imperfection
    if partial_imperf:
        note.addAttribute('num', str(ratio.denominator))
        note.addAttribute('numbase', str(ratio.numerator))

    return partial_imperf

# Performs the actual change, in notes and rests, from contemporary to mensural notation.  This involves 2 steps:
# 1. Note/Rest Shape part: Changes the @dur value to represent mensural figures
# 2. Note's Actual Duration part: Identifies which notes were 'perfected', 'imperfected' or 'altered' and indicates this with the attributes: @quality, @num and @numbase
def noterest_to_mensural(notes, rests, modusmaior, modusminor, tempus, prolatio, triplet_of_minims_flag):
    """
    Change the @dur attribute within the <note> and <rest> elements to a mensural-value; and add @num, @numbase and @quality attributes when appropriate.

    Arguments:
    notes -- list of all the <note> elements from a particular voice
    rests -- list of all the <rest> elements from a particular voice
    modusmaior, modusminor, tempus, prolatio -- integer values (3 or 2) that give the mensuration of the voice
    triplet_of_minims -- boolean flag that indicates the presence of a 'triplet of minims' in the piece (all voices)
    """
    list_values = imp_perf_vals(triplet_of_minims_flag, modusmaior, modusminor, tempus, prolatio)
    sb_def, sb_imp, sb_perf = list_values[0]
    b_def, b_imp, b_perf = list_values[1]
    l_def, l_imp, l_perf = list_values[2]
    max_def, max_imp, max_perf = list_values[3]
    smaller_notes = {'2': 'minima', '4': 'semiminima', '8': 'fusa', '16': 'semifusa'}

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
                # Check for partial imperfection, coloration, or mistakes
                ratio = Fraction(durges_num, max_def)
                partial_imp = partial_imperfection(note, ratio, modusmaior, modusminor, tempus)
                if partial_imp:
                    pass
                elif ratio == Fraction(2,3) and note.hasAttribute('color'):
                    note.addAttribute('num','3')
                    note.addAttribute('numbase','2')
                else:
                    print("This MAXIMA " + str(note) + " has an inappropriate duration @dur.ges = " + str(durges_num) + "p, as it is " + str(ratio.numerator) + "/" + str(ratio.denominator) + " part of its normal value.")

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
                # Check for partial imperfection, coloration, or mistakes
                ratio = Fraction(durges_num, l_def)
                partial_imp = partial_imperfection(note, ratio, modusminor, tempus, prolatio)
                if partial_imp:
                    pass
                elif ratio == Fraction(2,3) and note.hasAttribute('color'):
                    note.addAttribute('num','3')
                    note.addAttribute('numbase','2')
                else:
                    print("This LONG " + str(note) + " has an inappropriate duration @dur.ges = " + str(durges_num) + "p, as it is " + str(ratio.numerator) + "/" + str(ratio.denominator) + " part of its normal value.")

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
                # Check for partial imperfection, coloration, or mistakes
                ratio = Fraction(durges_num, b_def)
                partial_imp = partial_imperfection(note, ratio, tempus, prolatio)
                if partial_imp:
                    pass
                elif ratio == Fraction(2,3) and note.hasAttribute('color'):
                    note.addAttribute('num','3')
                    note.addAttribute('numbase','2')
                else:
                    print("This BREVE " + str(note) + " has an inappropriate duration @dur.ges = " + str(durges_num) + "p, as it is " + str(ratio.numerator) + "/" + str(ratio.denominator) + " part of its normal value.")

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
                print("This SEMIBREVE " + str(note) + " has an inappropriate duration @dur.ges = " + str(durges_num) + "p, as it is " + str(Fraction(durges_num, sb_def).numerator) + "/" + str(Fraction(durges_num, sb_def).denominator) + " part of its normal value.")

       # SMALLER NOTES (OR MISTAKE)
        else:
            # Notes smaller than the semibreve (i.e., minima, semiminima, fusa, and semifusa)
            try:
                mens_dur = smaller_notes[dur]
            # If this is not the case, we have an incorrect note value
            except:
                if dur != "TiedNote!":
                    print("This note shouldn't be here, as it is larger than a maxima or shorter than a minima! " + str(note) + ", " + str(dur) + ", " + str(durges_num) + "p")
                    mens_dur = dur
                else:
                    print("Still tied-note")
            # If the CMN note is dotted (@dots = 1), then its value is ternary, changing the default imperfect value of these smaller notes to perfect
            # Thus, we add @quality = 'p', and @num = '2' and @numbase = '3'
            if note.hasAttribute('dots') and note.getAttribute('dots').value == '1':
                note.addAttribute('quality', 'p')
                note.addAttribute('num', '2')
                note.addAttribute('numbase', '3')

        # Change the @dur value to the corresponding mensural note value
        note.getAttribute('dur').setValue(mens_dur)
        # And encode coloration if present in the note
        if note.hasAttribute('color'):
            note.addAttribute('colored', 'true')
            note.removeAttribute('color')


    # Rest's Part:
    # Rests can't be modified from its original value
    # Long-rests don't exist, there only is 1, 2 or 3 breve rests.
    for rest in rests:
        # Due to the mRest part of the code, all the rests have a @dur attribute.
        dur = rest.getAttribute('dur').value
        # Semibreve rest
        if dur == "1":
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
        else:
            # Notes smaller than the semibreve (i.e., minima, semiminima, fusa, and semifusa)
            try:
                mens_dur = smaller_notes[dur]
            # Mistake in rest's duration (@dur attribute)
            except:
                print("This kind of Rest shouldn't be in this repertory " + str(note) + ", it has a duration of  " + str(dur) + "\n")
                mens_dur = dur

        # Change the @dur value to the corresponding mensural note value
        rest.getAttribute('dur').setValue(mens_dur)
        # And encode coloration if present in the rest
        if rest.hasAttribute('color'):
            rest.addAttribute('colored', 'true')
            rest.removeAttribute('color')


def fill_section(out_section, all_voices, ids_removeList, input_doc):
    """
    Fill the <section> element of the Mensural-MEI document with the appropriate musical content.

    This function calls the noterest_to_mensural function to fill the <section> element with the right note (and rest) values.
    The appropriate musical content for the <section> in a Mensural-MEI document includes <note> and <rest> elements, but not <tuplet> or <tie> elements.

    Arguments:
    out_section -- the <section> element to be filled in
    all_voices -- list of lists, each sublist represents a particular voice in the CMN-MEI document and contains all the <staff> elements from that voice
    ids_removeList -- list of <note> elements that shouldn't be included in the Mensural-MEI output document (generally notes that are part of a tie)
    input_doc -- the pymei.MeiDocument that has all the CMN-MEI file information
    """
    flag_triplet_minims = False
    for ind_voice in all_voices:
        # Add a staff for each voice, with the id corresponding to the first <staff> element in the input_file for that exact voice
        staff = MeiElement('staff')
        old_staff = input_doc.getElementsByName('staff')[all_voices.index(ind_voice)]
        staff.setId(old_staff.id)
        staff.addAttribute(old_staff.getAttribute('n'))
        out_section.addChild(staff)
        # Add a layer inside the <staff> for each voice, with the id corresponding to the first <layer> element in the input_file for that exact voice
        layer = MeiElement('layer')
        old_layer = input_doc.getElementsByName('layer')[all_voices.index(ind_voice)]
        layer.setId(old_layer.id)
        layer.addAttribute(old_layer.getAttribute('n'))
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
                    # The only tuplets present in Ars Nova and are tuplets of minims
                    flag_triplet_minims = True
                    tuplet = element
                    num = int(tuplet.getAttribute('num').value)
                    numbase = int(tuplet.getAttribute('numbase').value)
                    notes_grouped = tuplet.getChildren()
                    for note in notes_grouped:
                        durges = note.getAttribute('dur.ges').value
                        actual_durges_num = int( int(durges[0:len(durges)-1]) * numbase / num )
                        actual_durges = str(actual_durges_num) + 'p'
                        note.getAttribute('dur.ges').setValue(actual_durges)
                        layer.addChild(note)
                        # Adding the <dot> element after a 'staccated' note or rest element
                        if note.hasAttribute('artic') and note.getAttribute('artic').value == "stacc":
                            layer.addChild(MeiElement('dot'))
                # Beams: In white notation there are already fusas and semifusas, represented by eighth and sixteenth notes, respectively, which can be beamed together
                elif element.name == 'beam':
                    beam = element
                    notes_grouped = beam.getChildren()
                    for note in notes_grouped:
                        layer.addChild(note)
                        # Adding the <dot> element after a 'staccated' note or rest element
                        if note.hasAttribute('artic') and note.getAttribute('artic').value == "stacc":
                            layer.addChild(MeiElement('dot'))
                # mRests
                elif element.name == 'mRest':
                    # Change into simple <rest> elements (as there are no measure-rests in mensural notation)
                    rest = MeiElement('rest')
                    rest.id = element.id
                    rest.setAttributes(element.getAttributes())
                    layer.addChild(rest)
                    # If there is no duration encoded in the rest, this mRest has the duration of the measure (which, generally, is a long)
                    if rest.hasAttribute('dur') == False:
                        rest.addAttribute('dur', 'breve')
                # Notes and simple rests
                else:
                    layer.addChild(element)

                # Adding the <dot> element after a 'staccated' note or rest element
                if element.hasAttribute('artic') and element.getAttribute('artic').value == "stacc":
                    layer.addChild(MeiElement('dot'))
            # Add barline
            layer.addChild(MeiElement('barLine'))

    return flag_triplet_minims

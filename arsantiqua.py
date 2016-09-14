"""
arsantiqua module

Contains all the relevant functions for translating Ars Antiqua pieces written in CMN-MEI to Mensural-MEI

Functions:
noterest_to_mensural -- Perform the actual change, in notes and rests, from contemporary to mensural notation
sb_major_minor -- Identify 'major semibreves' by adding @num, @numbase and @quality attributes to the note-element
fill_section -- Fill the output <section> element with the appropriate musical content
"""
# Ars Antiqua is characterized by the following:
# 1. Absence of 'minims' 
# 2. Absence of 'prolatio'
# 3. The 'breve' can't be identified as 'perfect' or 'imperfect'. 
#    It is just considered to be equal to 3 minor semibreves, or a pair of minor-major semibreves, 
#    or it is equal to 2 equal duration semibreves.
# 4. The fact that the 'breve' can't be catalogued as 'perfect' or 'imperfect', implies that the 'semibreve' can't be 'altered.
#    It just can't be 'major' or 'minor'.
# 5. There are no 'maximas' just 'duplex longas'
from fractions import *

from pymei import *


# Performs the actual change, in notes and rests, from contemporary to mensural notation.  This involves 2 steps:
# 1. Note/Rest Shape part: Changes the @dur value to represent mensural figures
# 2. Note's Actual Duration part: Identifies which notes were 'perfected', 'imperfected' or 'altered' and indicates this with the attributes: @quality, @num and @numbase
def noterest_to_mensural(notes, rests, modusminor):
    """
    Change the @dur attribute within the <note> and <rest> elements to a mensural-value; and add @num, @numbase and @quality attributes when appropriate.

    Arguments:
    notes -- list of all the <note> elements from a particular voice
    rests -- list of all the <rest> elements from a particular voice
    modusminor -- integer value of the modusminor from a particular voice
    """
    # Default values for notes according to the mensuration
    b_def = 2048
    
    l_def = modusminor * b_def
    l_imp = 2* b_def
    l_perf = 3 * b_def

    max_def = 2 * l_def
    # The default value of the 'maxima' is double because, actually, there is no maxima in this repertoire
    # Ars Antiqua has no 'maximas' just 'duplex longs'

    # Notes's Part:
    # Only breves can be altered (as only longs can be perfect/imperfect)
    # Breves can't be perfect/imperfect (they are always 3 minor-semibreves long)
    for note in notes:
        dur = note.getAttribute('dur').value
        durges_num = int(note.getAttribute('dur.ges').value[:-1])

        # For the tied notes:
        # First find its right (contemporary) duration
        if dur == 'TiedNote!':
            # Maximas
            if durges_num == max_def:
                dur = 'maxima'
            # Longas
            elif durges_num in [l_imp, l_perf]:
                dur = 'long'
            # MISTAKE in tie duration
            else:
                print("Weird\n The tied note doesn't seem to be any note in the range of longa to maxima - " + str(note) + ", its duration is " + str(durges_num) + "p")
            note.getAttribute('dur').setValue(dur)

        # Look for the corresponding mensural duration of the notes

        # MAXIMA (Duplex Longa)
        if dur == 'maxima':
            mens_dur = 'maxima'

        # LONGA
        elif dur == 'long':
            # Default @dur value of the note (Exception: Altered Breve)
            mens_dur = 'longa'

            # Looking for 'perfections', 'imperfections' and 'alterations'
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
            # MISTAKE on the note's duration
            else:
                print("This LONG note " + str(note) + " has an inappropriate duration @dur.ges = " + str(durges_num) + "p, as it is " + str(Fraction(durges_num, l_def).numerator) + "/" + str(Fraction(durges_num, l_def).denominator) + " part of its normal value.")

        # BREVIS
        elif dur == 'breve':
            mens_dur = 'brevis'

        # SEMIBREVIS
        elif dur == '1':
            mens_dur = 'semibrevis'

        # INCORRECT NOTE VALUE
        else:
            if dur != "TiedNote!":
                print("This note shouldn't be here, as it is larger than a maxima or shorter than a semibrevis! " + str(note) + ", " + str(dur) + ", " + str(durges_num) + "p")
                mens_dur = dur
            else:
                print("Still tied-note")

        # Change the @dur value to the corresponding mensural note value
        note.getAttribute('dur').setValue(mens_dur)

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
                if durges_num != 1024:
                    print("This SEMIBREVE rest " + str(rest) + ", doesn't have the appropriate @dur.ges value, as it is " + str(durges_num) + "p, instead of 1024p\n")
        # Breve rest
        elif dur == "breve":
            mens_dur = "brevis" # 1B rest??????????
            # Check for mistakes in duration (@dur.ges attribute)
            if rest.hasAttribute('dur.ges'):
                durges_num = int(rest.getAttribute('dur.ges').value[:-1])
                if durges_num != 2048:
                    print("This BREVE rest " + str(rest) + ", doesn't have the appropriate @dur.ges value, as it is " + str(durges_num) + "p, instead of 2048p\n")
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


# Finds and indicates which Semibreves are Major, completing the encoding of the "Note's Actual Duration" part.
def sb_major_minor(children_of_voiceStaff):
    """
    Add @quality, @num and @numbase attributes to indicate a 'major semibreve' (as opposed to a 'minor semibreve').

    Arguments:
    children_of_voiceStaff -- list of all the MeiElement objects contained in the <staff> element of a single voice, this includes: <tuplet>, <note> and <rest> elements.
    """
    indices_BrevesOrTuplets = [-1]
    for element in children_of_voiceStaff:
        if (element.name == 'tuplet') or (element.hasAttribute('dur') and (element.getAttribute('dur').value == 'brevis' or element.getAttribute('dur').value == 'longa' or element.getAttribute('dur').value == 'maxima')):
            indices_BrevesOrTuplets.append(children_of_voiceStaff.index(element))
    for i in range(0, len(indices_BrevesOrTuplets)-1):
        start = indices_BrevesOrTuplets[i]
        end = indices_BrevesOrTuplets[i+1]
        number_sb = end - start - 1
        # Case 1: Even number of semibreves
        if number_sb % 2 == 0:
            cont_sb = 0
            for j in range(start+1, end):
                cont_sb = cont_sb + 1
                # 2nd, 4th, 6th, ... semibreve in the sequence; generally, these are the ones that are Major (default case), but there are exceptions
                if cont_sb % 2 == 0:
                    previous_sb = children_of_voiceStaff[j-1]
                    # The exception: tenuto marks (downward stems) in the previous note (1st, 3rd, 5th, ... semibreve)
                    if previous_sb.hasAttribute('artic') and previous_sb.getAttribute('artic').value == 'ten':
                        previous_sb.addAttribute('quality', 'major')
                        previous_sb.addAttribute('num', '1')
                        previous_sb.addAttribute('numbase', '2')
                    # The default case:
                    else:
                        current_sb = children_of_voiceStaff[j]
                        current_sb.addAttribute('quality', 'major')
                        current_sb.addAttribute('num', '1')
                        current_sb.addAttribute('numbase', '2')
                else:
                    pass
        # Case 2: Odd number of semibreves
        else:
            # This can (should) only happen when there is a 2:1 tuplet at one extreme of the sequence of semibreves,
            # so that the whole tuplet is equal to just 1 minor semibreve,
            # and the semibreve that precedes/follows it (ususally has a downward stem to indicate its longer duration in the group) is the Major Semibreve that completes the Perfect Breve.
            # Without this grouping (major semibreve and tuplet), we are left with an even number of semibreves that can be grouped into minor-major pairs, as usual.
            start_element = children_of_voiceStaff[start]
            end_element = children_of_voiceStaff[end]
            # If the 2:1 tuplet precedes of the sequence of semibreves
            if (start_element.name == 'tuplet' and start_element.getAttribute('num').value == '2' and start_element.getAttribute('numbase').value == '1'):
                # The semibreve that follows this 2:1 tuplet should be major (completing the perfection)
                major_sb = children_of_voiceStaff[start + 1]
                major_sb.addAttribute('quality', 'major')
                major_sb.addAttribute('num', '1')
                major_sb.addAttribute('numbase', '2')
                # The other semibreves are grouped into minor-major pairs
                cont_sb = 0
                for j in range(start+2, end):
                    cont_sb = cont_sb + 1
                    # The second semibreve of each pair: generally it is Major (default case), but there are exceptions
                    if cont_sb % 2 == 0:
                        previous_sb = children_of_voiceStaff[j-1]
                        # The exception: tenuto marks (downward stems) in the previous note (1st, 3rd, 5th, ... semibreve)
                        if previous_sb.hasAttribute('artic') and previous_sb.getAttribute('artic').value == 'ten':
                            previous_sb.addAttribute('quality', 'major')
                            previous_sb.addAttribute('num', '1')
                            previous_sb.addAttribute('numbase', '2')
                        # The default case:
                        else:
                            current_sb = children_of_voiceStaff[j]
                            current_sb.addAttribute('quality', 'major')
                            current_sb.addAttribute('num', '1')
                            current_sb.addAttribute('numbase', '2')
                    # The first semibreve of each pair (it is generally minor, so we don't make any changes to it)
                    else:
                        pass
            # If the 2:1 tuplet follows the sequence of semibreves
            elif (end_element.name == 'tuplet' and end_element.getAttribute('num').value == '2' and end_element.getAttribute('numbase').value == '1'):
                # The semibreve that precedes the 2:1 tuplet, should be major (completing the perfection)
                major_sb = children_of_voiceStaff[end - 1]
                major_sb.addAttribute('quality', 'major')
                major_sb.addAttribute('num', '1')
                major_sb.addAttribute('numbase', '2')
                # The other semibreves are grouped into minor-major pairs
                cont_sb = 0
                for j in range(start+1, end-1):
                    cont_sb = cont_sb + 1
                    # The second semibreve of each pair: generally it is Major (default case), but there are exceptions
                    if cont_sb % 2 == 0:
                        previous_sb = children_of_voiceStaff[j-1]
                        # The exception: tenuto marks (downward stems) in the previous note (1st, 3rd, 5th, ... semibreve)
                        if previous_sb.hasAttribute('artic') and previous_sb.getAttribute('artic').value == 'ten':
                            previous_sb.addAttribute('quality', 'major')
                            previous_sb.addAttribute('num', '1')
                            previous_sb.addAttribute('numbase', '2')
                        # The default case:
                        else:
                            current_sb = children_of_voiceStaff[j]
                            current_sb.addAttribute('quality', 'major')
                            current_sb.addAttribute('num', '1')
                            current_sb.addAttribute('numbase', '2')
                    # The first semibreve of each pair (it is generally minor, so we don't make any changes to it)
                    else:
                        pass
            # Mistake case: If there is no tuplet 2:1 in any extreme, there shouldn't be an odd number of semibreves
            else:
                print("This shouldn't happen! \nThere is an odd number of semibreves between two perfect breves (or tuplets that are equivalent to a perfect breve), \nwhich doesn't allow to form minor-major (or major-minor) pairs of semibreves.")
                print("You can find these breves between the " + str(start_element.name) + " with id " + str(start_element.id) + " and the " + str(end_element.name) + " with id " + str(end_element.id))


def fill_section(out_section, all_voices, ids_removeList, input_doc, breve_choice):
    """
    Fill the <section> element of the Mensural-MEI document with the appropriate musical content.

    This function calls the other two functions (noterest_to_mensural and sb_major_minor) to fill the <section> element with the right note (and rest) values.
    The appropriate musical content for the <section> in a Mensural-MEI document includes <note> and <rest> elements, but not <tuplet> or <tie> elements.

    Arguments:
    out_section -- the <section> element to be filled in
    all_voices -- list of lists, each sublist represents a particular voice in the CMN-MEI document and contains all the <staff> elements from that voice
    ids_removeList -- list of <note> elements that shouldn't be included in the Mensural-MEI output document (generally notes that are part of a tie)
    input_doc -- the pymei.MeiDocument that has all the CMN-MEI file information
    breve_choice -- string that indicates the division of the breve: '3' or '2'
    """
    # List of lists, each of them with all the elements of one voice
    voices_elements = []
    # Filling the section element:
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
        # Ordered list of all the elements of one voice (<note>, <rest> and <tuplet>), useful for identifying the 'Major Semibreves' of the voice
        elements_per_voice = []
        # Fill each voice (fill the <layer> of each <staff>) with musical information (notes/rests)
        for i in range(0, len(ind_voice)):
            musical_content = ind_voice[i].getChildrenByName('layer')[0].getChildren()
            # Add the elements of each measure into the <layer> and a <barLine/> element after the measure-content
            for element in musical_content:
                # Tied notes
                # If the element is a tied note (other than the first note of the tie: <note @dur = 'TiedNote!'>), it is not included in the output file (as only the first tied note will be included with the right note shape and duration -@dur.ges-)
                if element.id in ids_removeList:
                    pass
                # Tuplets
                elif element.name == 'tuplet':
                    # Add the <tuplet> to the list of elements in the voice
                    elements_per_voice.append(element)
                    # The only tuplets present in Ars Antiqua are tuplets of semibreves
                    tuplet = element
                    num = int(tuplet.getAttribute('num').value)
                    numbase = int(tuplet.getAttribute('numbase').value)
                    # @numbase is usually '2', because generally a breve = 3 minor semibreves, so tuplets of 3:2 are frequently used to represent 3 (minor) semibreves per breve.
                    # There are also other cases in which we have more than 3 semibreves per breve: 4:2, 5:2, 6:2 and 7:2
                    if numbase == 2:
                        base = int(breve_choice)
                    # There is also the case of 2:1 tuplets, in which case @numbase = '1', to indicate a group of two semibreves which should be interpreted as one minor semibreve
                    elif numbase == 1:
                        base = 1
                    else:
                        print("Shouldn't happen!")
                    # Find the simplified ratio between @numbase and @num 
                    notes_grouped = tuplet.getChildren()
                    durRatio = Fraction(base, num)
                    # If the ratio isn't 1, add the simplified @num and @numbase attributes to each of the notes in the tuplet
                    # And add each note to the <layer> of the voice
                    if durRatio == 1:
                        for note in notes_grouped:
                            layer.addChild(note)
                    else:
                        notes_grouped = tuplet.getChildren()
                        for note in notes_grouped:
                            note.addAttribute('num', str(durRatio.denominator))
                            note.addAttribute('numbase', str(durRatio.numerator))
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
                    # Add the <rest> to the list of elements in the voice
                    elements_per_voice.append(rest)
                # Notes and simple rests
                else:
                    layer.addChild(element)
                    # Add the <note> or <rest> to the list of elements in the voice
                    elements_per_voice.append(element)
            # Add barline
            layer.addChild(MeiElement('barLine'))
        # Completing the list of lists with the mei-elements of each voice
        voices_elements.append(elements_per_voice)

    return voices_elements
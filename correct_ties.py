from pymei import *
from os import listdir, path


# --------- #
# Functions #
# --------- #
def identify_endnote(start_note):
    peers = start_note.getPeers()

    # If the last note in the measure is the staring note of the tie,
    # we are dealing with an inter-measure tie
    if peers[-1] == start_note:
        # Get the next measure
        start_measure_n = int(start_note.getAncestor('measure').getAttribute('n').value)
        end_measure = doc.getElementsByName('measure')[start_measure_n]

        # Get the right staff number (the same as the start_note)
        start_staff_n = int(start_note.getAncestor('staff').getAttribute('n').value)
        staff = end_measure.getChildrenByName('staff')[start_staff_n - 1]
        first_note_endmeasure = staff.getChildrenByName('layer')[0].getChildrenByName('note')[0]
        endid = first_note_endmeasure.id
        tie.addAttribute('endid', '#' + endid)

    # If the beginning of the tie is at any place but the end of the measure
    # We are dealing with an intra-measure tie
    else:
        cont = 0
        for item in peers:
            if item == start_note:
                break
            cont = cont + 1
        next_note = peers[cont + 1]
        endid = next_note.id
        tie.addAttribute('endid', '#' + endid)


# ----------- #
# Main Script #
# ----------- #
directory = raw_input("Insert directory: ")
files = listdir(directory)
destination = raw_input("Destination: ")

for file in files:
    if file.endswith('.mei'):
        doc = documentFromFile(path.join(directory, file)).getMeiDocument()
        ties = doc.getElementsByName('tie')

        for tie in ties:
            startid = tie.getAttribute('startid').value[1:]
            start_note = doc.getElementById(startid)

            # If there is no ending note for the tie
            if not tie.hasAttribute('endid'):
                identify_endnote(start_note)

            # If there is an ending note, evaluate if it is right or wrong (e.g. it is on another staff)
            else:
                start_staff_n = int(start_note.getAncestor('staff').getAttribute('n').value)

                endid = tie.getAttribute('endid').value[1:]
                end_note = doc.getElementById(endid)
                end_staff_n = int(end_note.getAncestor('staff').getAttribute('n').value)

                # Correct! (if the tie starts and end in the same staff)
                if start_staff_n == end_staff_n:
                    pass
                # If the tie goes across staves
                else:
                    identify_endnote(start_note)

        documentToFile(doc, path.join(destination, file))

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('piece')
parser.add_argument('which_ars', choices=['ArsNova', 'ArsAntiqua'], help="If you select 'ArsNova' you have to use the optional argument '-newVoiceN' to add the mensuration (values for: modusmajor, modusminor, tempus and prolatio) for each voice. If you choose 'ArsAntiqua' you have to use the optional argument '-newVoiceA' to add the mensuration (values for: breve and modusminor) for each voice.")
parser.add_argument('--newvoice_nova', nargs=4, action='append') # for now, just 4 values per voice are allowed
parser.add_argument('--newvoice_antiqua', nargs=2, action='append', choices=[['3', 'p'], ['3', 'i'], ['2', 'p'], ['2', 'i']]) # for now, you have to add each voice
args = parser.parse_args()
print(args)
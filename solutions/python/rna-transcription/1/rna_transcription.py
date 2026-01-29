

def to_rna(dna_strand):
    string = ""
    for x in dna_strand:
        if x == "A":
            string += "U"
        elif x == "G":
            string += "C"
        elif x == "C":
            string += "G"
        elif x == "T":
            string += "A"
        else:
            string += x
    return string
        



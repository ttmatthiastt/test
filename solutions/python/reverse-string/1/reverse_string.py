def reverse(text):
    rev = ""
    for i in range (len(text)):
        rev += text[-(i+1)]
    return rev
        

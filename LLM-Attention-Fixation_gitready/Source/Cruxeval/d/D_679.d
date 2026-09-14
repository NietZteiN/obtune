import std.math;
import std.typecons;
import std.ascii;

bool f(string text) 
{
    if (text == "") {
        return false;
    }
    
    char firstChar = text[0];
    
    if (firstChar.isDigit) {
        return false;
    }
    
    foreach (char lastChar; text) {
        if ((lastChar != '_') && !isAlphaNum(lastChar)) {
            return false;
        }
    }
    
    return true;
}
unittest
{
    alias candidate = f;

    assert(candidate("meet") == true);
}
void main(){}

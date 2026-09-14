import std.math;
import std.typecons;
import std.string;

string f(string text, string letter) 
{
    if (('a' <= letter[0]) && (letter[0] <= 'z')) {
        letter = letter.toUpper();
    }
    text = text.replace(letter.toLower(), letter);
    return text.capitalize();
}
unittest
{
    alias candidate = f;

    assert(candidate("E wrestled evil until upperfeat", "e") == "E wrestled evil until upperfeat");
}
void main(){}

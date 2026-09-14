import std.math;
import std.typecons;
import std.string;
import std.ascii;

string f(string text) 
{
    string new_text = "";
    foreach (i, c; text)
    {
        if (isUpper(c))
        {
            new_text = new_text[0 .. new_text.length / 2] ~ c ~ new_text[new_text.length / 2 .. $];
        }
    }
    if (new_text.empty)
    {
        new_text = "-";
    }
    return new_text;
}
unittest
{
    alias candidate = f;

    assert(candidate("String matching is a big part of RexEx library.") == "RES");
}
void main(){}

import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.range;
import std.string;

string f(string text, string strip_chars) 
{
    auto reversedText = text.retro.strip(strip_chars);
    return reversedText.retro;
}
unittest
{
    alias candidate = f;

    assert(candidate("tcmfsmj", "cfj") == "tcmfsm");
}
void main(){}

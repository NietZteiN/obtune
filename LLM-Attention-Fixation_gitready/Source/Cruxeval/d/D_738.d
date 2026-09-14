import std.math;
import std.typecons;
import std.string;

string f(string text, string characters) 
{
    foreach(i; 0 .. characters.length)
    {
        text = text.stripRight(characters[i .. $]);
    }
    return text;
}
unittest
{
    alias candidate = f;

    assert(candidate("r;r;r;r;r;r;r;r;r", "x.r") == "r;r;r;r;r;r;r;r;");
}
void main(){}

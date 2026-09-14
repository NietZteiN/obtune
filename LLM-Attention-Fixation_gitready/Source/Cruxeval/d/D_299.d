import std.math;
import std.typecons;
import std.string;

string f(string text, string character) 
{
    if (!text.endsWith(character))
        return f(character ~ text, character);
    return text;
}
unittest
{
    alias candidate = f;

    assert(candidate("staovk", "k") == "staovk");
}
void main(){}

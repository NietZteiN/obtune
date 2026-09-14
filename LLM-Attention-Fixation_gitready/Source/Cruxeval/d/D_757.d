import std.math;
import std.typecons;
import std.string;

string f(string text, string character, string replace) 
{
    return text.replace(character, replace);
}
unittest
{
    alias candidate = f;

    assert(candidate("a1a8", "1", "n2") == "an2a8");
}
void main(){}

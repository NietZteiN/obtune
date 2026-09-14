import std.math;
import std.typecons;
import std.array;
import std.algorithm;
import std.string;

string[] f(string text, string sep) 
{
    auto words = text.split(sep);
    return words[0..$].array;
}
unittest
{
    alias candidate = f;

    assert(candidate("a-.-.b", "-.") == ["a", "", "b"]);
}
void main(){}

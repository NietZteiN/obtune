import std.math;
import std.typecons;
import std.string;
import std.algorithm;

string f(string text, long count) 
{
    foreach (immutable i; 0 .. count)
    {
        text = text.dup.reverse;
    }
    return text;
}
unittest
{
    alias candidate = f;

    assert(candidate("aBc, ,SzY", 2L) == "aBc, ,SzY");
}
void main(){}

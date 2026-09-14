import std.math;
import std.typecons;
import std.algorithm;
import std.range;
import std.string;

string f(string text) 
{
    for (size_t i = 0; i < text.length; i++)
    {
        if (text[0 .. i].startsWith("two"))
        {
            return text[i .. $];
        }
    }
    
    return "no";
}
unittest
{
    alias candidate = f;

    assert(candidate("2two programmers") == "no");
}
void main(){}

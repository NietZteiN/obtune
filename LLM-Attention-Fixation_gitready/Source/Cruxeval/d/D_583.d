import std.math;
import std.typecons;
import std.string;
import std.algorithm;
import std.conv;

string f(string text, string ch) 
{
    string[] lines = text.splitLines;
    string[] result;
    foreach (line; lines)
    {
        if (line.length > 0 && line[0] == ch[0])
        {
            result ~= line.toLower();
        }
        else
        {
            result ~= line.toUpper();
        }
    }
    return result.join("\n");
}
unittest
{
    alias candidate = f;

    assert(candidate("t
za
a", "t") == "t
ZA
A");
}
void main(){}

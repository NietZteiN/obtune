import std.math;
import std.typecons;
import std.string;
import std.algorithm;
import std.array;

string f(string text) 
{
    text = text.replace("#", "1").replace("$", "5");
    foreach (i, c; text)
    {
        if (!(c >= '0' && c <= '9'))
            return "no";
    }
    return "yes";
}
unittest
{
    alias candidate = f;

    assert(candidate("A") == "no");
}
void main(){}

import std.math;
import std.typecons;
import std.algorithm;
import std.ascii;
import std.conv;

string f(string text) 
{
    if (text.length != 0 && all!(a => isDigit(a))(text))
    {
        return "integer";
    }
    return "string";
}
unittest
{
    alias candidate = f;

    assert(candidate("") == "string");
}
void main(){}

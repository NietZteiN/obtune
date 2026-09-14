import std.math;
import std.typecons;
import std.string;
import std.algorithm;
import std.range;

string f(string s, string ch) 
{
    if (!ch.canFind(s))
    {
        return "";
    }
    s = s.split(ch)[1][$ - 1 .. $];
    foreach (i; 0 .. s.length)
    {
        s = s.split(ch)[1][$ - 1 .. $];
    }
    return s;
}
unittest
{
    alias candidate = f;

    assert(candidate("shivajimonto6", "6") == "");
}
void main(){}

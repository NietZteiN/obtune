import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.string;

string f(string text, string chars) 
{
    string result = text;
    while (result[$-3 .. $-1] == chars) {
        result = result[0 .. $-3] ~ result[$ .. $];
    }
    return result.stripRight(".");
}
unittest
{
    alias candidate = f;

    assert(candidate("ellod!p.nkyp.exa.bi.y.hain", ".n.in.ha.y") == "ellod!p.nkyp.exa.bi.y.hain");
}
void main(){}

import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.string;

string f(string s, string o) 
{
    if (s.startsWith(o))
        return s;
    return o ~ f(s, o[o.length - 2 .. $].idup);
}
unittest
{
    alias candidate = f;

    assert(candidate("abba", "bab") == "bababba");
}
void main(){}

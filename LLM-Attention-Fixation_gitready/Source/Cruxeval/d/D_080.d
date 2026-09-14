import std.math;
import std.typecons;
import std.array;
import std.algorithm;
import std.string;

string f(string s) 
{
    s = s.replace(" ", "");
    auto reversed_s = s.dup.reverse;
    return reversed_s.idup;
}
unittest
{
    alias candidate = f;

    assert(candidate("ab        ") == "ba");
}
void main(){}

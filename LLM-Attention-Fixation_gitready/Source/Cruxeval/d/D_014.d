import std.math;
import std.typecons;
import std.algorithm;
import std.range;
import std.string;

string f(string s) 
{
    auto arr = s.strip().dup;
    arr.reverse();
    return arr.idup;
}
unittest
{
    alias candidate = f;

    assert(candidate("   OOP   ") == "POO");
}
void main(){}

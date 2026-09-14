import std.math;
import std.typecons;
import std.string;
import std.algorithm;

string f(string match, string fill, long n) 
{
    return fill[0 .. min(n, fill.length)] ~ match;
}
unittest
{
    alias candidate = f;

    assert(candidate("9", "8", 2L) == "89");
}
void main(){}

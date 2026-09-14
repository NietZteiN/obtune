import std.math;
import std.typecons;
import std.algorithm;
import std.string;

bool f(string s, string n) 
{
    return equal(s.toLower(), n.toLower());
}
unittest
{
    alias candidate = f;

    assert(candidate("daaX", "daaX") == true);
}
void main(){}

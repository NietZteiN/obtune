import std.math;
import std.typecons;
import std.array;

string f(string s) 
{
    s = s.replace("(", "[").replace(")", "]");
    return s;
}
unittest
{
    alias candidate = f;

    assert(candidate("(ac)") == "[ac]");
}
void main(){}

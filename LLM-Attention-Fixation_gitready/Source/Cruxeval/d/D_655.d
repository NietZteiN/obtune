import std.math;
import std.typecons;
import std.array;

string f(string s) 
{
    s = s.replace("a", "").replace("r", "");
    return s;
}
unittest
{
    alias candidate = f;

    assert(candidate("rpaar") == "p");
}
void main(){}

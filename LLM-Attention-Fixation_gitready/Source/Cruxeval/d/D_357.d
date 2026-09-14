import std.math;
import std.typecons;
string f(string s) 
{
    string result;
    foreach (i; 0 .. s.length)
    {
        result = s[i] ~ result;
    }
    return result;
}
unittest
{
    alias candidate = f;

    assert(candidate("crew") == "werc");
}
void main(){}

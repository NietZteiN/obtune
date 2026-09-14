import std.math;
import std.typecons;
import std.string;

bool f(string s1, string s2) 
{
    foreach (k; 0 .. s2.length + s1.length)
    {
        s1 ~= s1[0];
        if (s1.indexOf(s2) >= 0)
            return true;
    }
    return false;
}
unittest
{
    alias candidate = f;

    assert(candidate("Hello", ")") == false);
}
void main(){}

import std.math;
import std.typecons;
string f(string s1, string s2) 
{
    if (s2[$-s1.length .. $] == s1) {
        s2 = s2[0 .. $-s1.length];
    }
    return s2;
}
unittest
{
    alias candidate = f;

    assert(candidate("he", "hello") == "hello");
}
void main(){}

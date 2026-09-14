import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.string;

string f(string s, string suffix) 
{
    if (suffix.length == 0) {
        return s;
    }
    while (s.endsWith(suffix)) {
        s = s[0 .. $ - suffix.length];
    }
    return s;
}
unittest
{
    alias candidate = f;

    assert(candidate("ababa", "ab") == "ababa");
}
void main(){}

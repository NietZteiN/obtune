import std.math;
import std.typecons;
import std.string;

string f(string s, string ch) {
    size_t count = s.count(ch) + 1;
    string base;
    foreach (i; 0 .. count) {
        base ~= ch;
    }
    return s.endsWith(base) ? s[0 .. $ - base.length] : s;
}

unittest
{
    alias candidate = f;

    assert(candidate("mnmnj krupa...##!@#!@#$$@##", "@") == "mnmnj krupa...##!@#!@#$$@##");
}
void main(){}

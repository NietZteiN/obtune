import std.math;
import std.typecons;
import std.string;

string f(string s) {
    auto pos = s.lastIndexOf("ar");
    if (pos == -1) {
        return s;
    }
    string before = s[0 .. pos];
    string sep = s[pos .. pos + 2];
    string after = s[pos + 2 .. $];
    return before ~ " " ~ sep ~ " " ~ after;
}

unittest
{
    alias candidate = f;

    assert(candidate("xxxarmmarxx") == "xxxarmm ar xx");
}
void main(){}

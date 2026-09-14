import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.string;

string f(string n, string s) 
{
    if (s.startsWith(n)) {
        auto pre = s[0 .. s.indexOf(n)];
        return pre ~ n ~ s[s.length-n.length .. $];
    }
    return s;
}
unittest
{
    alias candidate = f;

    assert(candidate("xqc", "mRcwVqXsRDRb") == "mRcwVqXsRDRb");
}
void main(){}

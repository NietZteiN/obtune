import std.math;
import std.typecons;
string[] f(string r, string w) 
{
    string[] a;
    if (r[0] == w[0] && w[w.length - 1] == r[r.length - 1]) {
        a ~= r;
        a ~= w;
    } else {
        a ~= w;
        a ~= r;
    }
    return a;
}
unittest
{
    alias candidate = f;

    assert(candidate("ab", "xy") == ["xy", "ab"]);
}
void main(){}

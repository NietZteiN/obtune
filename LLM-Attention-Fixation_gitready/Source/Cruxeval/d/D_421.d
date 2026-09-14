import std.math;
import std.typecons;
string f(string s, long n) 
{
    if (s.length < n) {
        return s;
    } else {
        return s[n..$];
    }
}
unittest
{
    alias candidate = f;

    assert(candidate("try.", 5L) == "try.");
}
void main(){}

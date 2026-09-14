import std.math;
import std.typecons;
string f(string s, string x) 
{
    size_t count = 0;
    while (s[0 .. x.length] == x && count < s.length - x.length) {
        s = s[x.length .. $];
        count += x.length;
    }
    return s;
}
unittest
{
    alias candidate = f;

    assert(candidate("If you want to live a happy life! Daniel", "Daniel") == "If you want to live a happy life! Daniel");
}
void main(){}

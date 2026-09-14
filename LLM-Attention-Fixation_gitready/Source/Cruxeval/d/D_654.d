import std.math;
import std.typecons;
import std.string;
import std.algorithm;

string f(string s, string from_c, string to_c) 
{
    if (from_c.length != to_c.length) {
        throw new Exception("Length of 'from_c' and 'to_c' must be the same.");
    }

    string result = s.dup;
    for (size_t i = 0; i < from_c.length; ++i) {
        result = result.replace(from_c[i], to_c[i]);
    }
    return result;
}
unittest
{
    alias candidate = f;

    assert(candidate("aphid", "i", "?") == "aph?d");
}
void main(){}

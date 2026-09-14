import std.math;
import std.typecons;
string[] f(string s, long[] characters) 
{
    string[] result;
    foreach (i; characters) {
        result ~= s[i .. i+1];
    }
    return result;
}
unittest
{
    alias candidate = f;

    assert(candidate("s7 6s 1ss", [1L, 3L, 6L, 1L, 2L]) == ["7", "6", "1", "7", " "]);
}
void main(){}

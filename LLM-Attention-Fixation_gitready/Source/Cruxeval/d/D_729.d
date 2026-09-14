import std.math;
import std.typecons;
import std.algorithm;
import std.array;

long[] f(string s1, string s2) 
{
    long[] res;
    long i = s1.length - s2.length;
    while(i >= 0) {
        if (s1[i .. i + s2.length] == s2) {
            res ~= i + s2.length - 1;
            i -= s2.length;
        } else {
            i--;
        }
    }
    return res;
}
unittest
{
    alias candidate = f;

    assert(candidate("abcdefghabc", "abc") == [10L, 2L]);
}
void main(){}

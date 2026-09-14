import std.math;
import std.typecons;
string f(string text, long m, long n) 
{
    text = text ~ text[0..m] ~ text[n..$];
    string result = "";
    foreach (i; n .. text.length - m)
    {
        result = text[i] ~ result;
    }
    return result;
}
unittest
{
    alias candidate = f;

    assert(candidate("abcdefgabc", 1L, 2L) == "bagfedcacbagfedc");
}
void main(){}

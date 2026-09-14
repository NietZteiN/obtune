import std.math;
import std.typecons;
import std.string;
import std.algorithm;

string f(string s, long encryption) 
{
    if (encryption == 0)
        return s;

    s = s.toUpper();
    string result = "";
    foreach (char c; s)
    {
        if ('A' <= c && c <= 'Z')
        {
            result ~= ((c - 'A' + 13) % 26) + 'A';
        }
        else
        {
            result ~= c;
        }
    }
    return result;
}
unittest
{
    alias candidate = f;

    assert(candidate("UppEr", 0L) == "UppEr");
}
void main(){}

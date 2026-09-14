import std.math;
import std.typecons;
import std.string;
string f(string s) 
{
    string result = "";
    foreach (char c; s)
    {
        result ~= toLower(c);
    }
    return result;
}
unittest
{
    alias candidate = f;

    assert(candidate("abcDEFGhIJ") == "abcdefghij");
}
void main(){}

import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.string;

long f(string s) 
{
    string b = "";
    string c = "";
    foreach (char i; s)
    {
        c ~= i;
        if (s.lastIndexOf(c) > -1)
        {
            return s.lastIndexOf(c);
        }
    }
    return 0;
}
unittest
{
    alias candidate = f;

    assert(candidate("papeluchis") == 2L);
}
void main(){}

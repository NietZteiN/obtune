import std.math;
import std.typecons;
import std.stdio;

string f(string s) 
{
    foreach (char c; s)
    {
        if (!(c >= '0' && c <= '9') && !(c >= 'A' && c <= 'Z') && !(c >= 'a' && c <= 'z'))
            return "False";
    }
    return "True";
}
unittest
{
    alias candidate = f;

    assert(candidate("777") == "True");
}
void main(){}

import std.math;
import std.typecons;
import std.ascii;
import std.array;
import std.conv;

long f(string text) 
{
    string[] a = [""];
    string b = "";
    foreach (char i; text)
    {
        if (!isWhite(i))
        {
            a ~= b;
            b = "";
        }
        else
        {
            b ~= i;
        }
    }
    return to!int(a.length);
}
unittest
{
    alias candidate = f;

    assert(candidate("       ") == 1L);
}
void main(){}

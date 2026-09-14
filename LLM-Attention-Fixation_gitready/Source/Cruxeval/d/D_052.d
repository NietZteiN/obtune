import std.math;
import std.typecons;
import std.range;
import std.conv;

string f(string text) 
{
    string a;
    foreach (i; 0 .. text.length)
    {
        if (!('0' <= text[i] && text[i] <= '9'))
        {
            a ~= text[i];
        }
    }
    return a;
}
unittest
{
    alias candidate = f;

    assert(candidate("seiq7229 d27") == "seiq d");
}
void main(){}

import std.math;
import std.typecons;
string f(string text) 
{
    string result = "";
    foreach (i; 0 .. text.length)
    {
        result = text[i] ~ result;
    }
    return result;
}
unittest
{
    alias candidate = f;

    assert(candidate("was,") == ",saw");
}
void main(){}

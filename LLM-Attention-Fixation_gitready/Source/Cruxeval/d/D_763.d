import std.math;
import std.typecons;
import std.string;

string f(string values, string text, string markers) 
{
    return text.stripRight(values).stripRight(markers);
}
unittest
{
    alias candidate = f;

    assert(candidate("2Pn", "yCxpg2C2Pny2", "") == "yCxpg2C2Pny");
}
void main(){}

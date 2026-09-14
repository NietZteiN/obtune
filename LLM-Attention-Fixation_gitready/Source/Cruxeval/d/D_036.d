import std.math;
import std.typecons;
import std.string;

string f(string text, string chars) 
{
    if (text.empty)
    {
        return text;
    }
    else
    {
        return text.stripRight(chars);
    }
}
unittest
{
    alias candidate = f;

    assert(candidate("ha", "") == "ha");
}
void main(){}

import std.math;
import std.typecons;
import std.conv;

bool f(string text) 
{
    bool isNumeric;
    try
    {
        text.to!long;
        isNumeric = true;
    }
    catch (ConvException)
    {
        isNumeric = false;
    }
    return !isNumeric;
}
unittest
{
    alias candidate = f;

    assert(candidate("the speed is -36 miles per hour") == true);
}
void main(){}

import std.math;
import std.typecons;
import std.conv;

bool f(string number) 
{
    try
    {
        number.to!long;
        return true;
    }
    catch (ConvException)
    {
        return false;
    }
}
unittest
{
    alias candidate = f;

    assert(candidate("dummy33;d") == false);
}
void main(){}

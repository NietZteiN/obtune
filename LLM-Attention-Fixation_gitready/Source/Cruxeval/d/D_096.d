import std.math;
import std.typecons;
import std.ascii;

bool f(string text) 
{
    foreach (c; text)
    {
        if (isUpper(c))
        {
            return false;
        }
    }
    return true;
}
unittest
{
    alias candidate = f;

    assert(candidate("lunabotics") == true);
}
void main(){}

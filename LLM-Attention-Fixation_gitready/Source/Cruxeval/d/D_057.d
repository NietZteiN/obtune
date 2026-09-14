import std.math;
import std.typecons;
import std.string;

long f(string text) 
{
    auto upperCount = 0;
    foreach (c; text.toUpper())
    {
        if (c == c.toUpper())
        {
            upperCount++;
        }
        else
        {
            return -1;
        }
    }
    return upperCount / 2;
}
unittest
{
    alias candidate = f;

    assert(candidate("ax") == 1L);
}
void main(){}

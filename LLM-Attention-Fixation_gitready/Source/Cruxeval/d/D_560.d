import std.math;
import std.typecons;
import std.ascii;

long f(string text) 
{
    long x = 0;
    foreach (c; text)
    {
        if (isLower(c))
        {
            x++;
        }
    }
    return x;
}
unittest
{
    alias candidate = f;

    assert(candidate("591237865") == 0L);
}
void main(){}

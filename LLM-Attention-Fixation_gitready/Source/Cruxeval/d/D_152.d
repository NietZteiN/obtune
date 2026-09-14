import std.math;
import std.typecons;
import std.uni : isUpper;

long f(string text) 
{
    long n = 0;
    foreach (c; text)
    {
        if (isUpper(c))
        {
            n++;
        }
    }
    return n;
}
unittest
{
    alias candidate = f;

    assert(candidate("AAAAAAAAAAAAAAAAAAAA") == 20L);
}
void main(){}

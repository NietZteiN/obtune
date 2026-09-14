import std.math;
import std.typecons;
import std.algorithm;
import std.array;

long f(string text, string sub) 
{
    long a = 0;
    long b = text.length - 1;

    while (a <= b)
    {
        long c = (a + b) / 2;
        if (text.endsWith(sub, c))
        {
            a = c + 1;
        }
        else
        {
            b = c - 1;
        }
    }

    return a;
}
unittest
{
    alias candidate = f;

    assert(candidate("dorfunctions", "2") == 0L);
}
void main(){}

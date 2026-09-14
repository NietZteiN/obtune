import std.math;
import std.typecons;
import std.ascii;

long f(string text) 
{
    long number = 0;
    foreach (char t; text)
    {
        if (isDigit(t))
        {
            number++;
        }
    }
    return number;
}
unittest
{
    alias candidate = f;

    assert(candidate("Thisisastring") == 0L);
}
void main(){}

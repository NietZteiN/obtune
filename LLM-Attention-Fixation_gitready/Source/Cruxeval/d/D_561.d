import std.math;
import std.typecons;
import std.conv;

long f(string text, string digit) 
{
    long count = 0;
    foreach (char c; text)
    {
        if (c == digit[0])
        {
            count++;
        }
    }
    return to!long(digit) * count;
}
unittest
{
    alias candidate = f;

    assert(candidate("7Ljnw4Lj", "7") == 7L);
}
void main(){}

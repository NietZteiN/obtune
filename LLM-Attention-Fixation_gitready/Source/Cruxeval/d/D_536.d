import std.math;
import std.typecons;
import std.ascii;

long f(string cat) 
{
    long digits = 0;
    foreach (char c; cat)
    {
        if (isDigit(c))
        {
            digits++;
        }
    }
    return digits;
}
unittest
{
    alias candidate = f;

    assert(candidate("C24Bxxx982ab") == 5L);
}
void main(){}

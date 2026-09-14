import std.math;
import std.typecons;
import std.array;
import std.string;

long f(string text) 
{
    auto k = text.splitLines();
    long i = 0;
    foreach (j; k)
    {
        if (j.length == 0)
            return i;
        i++;
    }
    return -1;
}
unittest
{
    alias candidate = f;

    assert(candidate("2 m2 

bike") == 1L);
}
void main(){}

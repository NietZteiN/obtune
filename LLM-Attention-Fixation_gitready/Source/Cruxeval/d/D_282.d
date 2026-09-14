import std.math;
import std.typecons;
import std.string;

long f(string s1, string s2) 
{
    long position = 1;
    long count = 0;
    while (position > 0)
    {
        position = s1.indexOf(s2, position);
        count += 1;
        position += 1;
    }
    return count;
}
unittest
{
    alias candidate = f;

    assert(candidate("xinyyexyxx", "xx") == 2L);
}
void main(){}

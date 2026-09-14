import std.math;
import std.typecons;
import std.conv;
import std.string;

long f(string x) 
{
    long a = 0;
    foreach (i; x.split())
    {
        a += i.length * 2;
    }
    return a;
}
unittest
{
    alias candidate = f;

    assert(candidate("999893767522480") == 30L);
}
void main(){}

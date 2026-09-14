import std.math;
import std.typecons;
import std.range;

long[] f(long[] list) 
{
    auto original = list;
    while (list.length > 1)
    {
        list.length--;
        foreach (i; 0 .. list.length)
        {
            list = list[0 .. i] ~ list[i+1 .. $];
        }
    }
    list = original;
    if (list.length > 0)
    {
        list = list[1 .. $];
    }
    return list;
}
unittest
{
    alias candidate = f;

    assert(candidate([]) == []);
}
void main(){}

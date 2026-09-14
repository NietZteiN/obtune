import std.math;
import std.typecons;
import std.algorithm;
import std.range;

long f(long[] array, long elem) 
{
    return count(array, elem) + elem;
}

long count(R)(R range, long elem)
{
    long count = 0;
    foreach (element; range)
    {
        if (element == elem)
        {
            count++;
        }
    }
    return count;
}
unittest
{
    alias candidate = f;

    assert(candidate([1L, 1L, 1L], -2L) == -2L);
}
void main(){}

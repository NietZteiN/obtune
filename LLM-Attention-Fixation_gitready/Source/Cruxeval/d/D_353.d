import std.math;
import std.typecons;
import std.array;
import std.algorithm;

long f(long[] x) 
{
    if (x.empty)
        return -1;
    long[long] cache;
    foreach (item; x) 
    {
        if (item in cache) 
        {
            cache[item]++;
        } 
        else 
        {
            cache[item] = 1;
        }
    }
    return cache.values.maxElement;
}
unittest
{
    alias candidate = f;

    assert(candidate([1L, 0L, 2L, 2L, 0L, 0L, 0L, 1L]) == 4L);
}
void main(){}

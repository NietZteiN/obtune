import std.math;
import std.typecons;
import std.algorithm;
import std.range;

long f(long[] in_list, long num) 
{
    in_list ~= num;
    long maxIndex = -1;
    long maxValue = -1;
    foreach (i, value; in_list[0 .. $-1].enumerate)
    {
        if (value > maxValue)
        {
            maxValue = value;
            maxIndex = i;
        }
    }
    return maxIndex;
}
unittest
{
    alias candidate = f;

    assert(candidate([-1L, 12L, -6L, -2L], -1L) == 1L);
}
void main(){}

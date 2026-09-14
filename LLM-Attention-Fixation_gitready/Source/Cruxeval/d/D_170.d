import std.math;
import std.typecons;
import std.stdio;

long f(long[] nums, long number) 
{
    long count = 0;
    foreach (num; nums)
    {
        if (num == number)
        {
            count++;
        }
    }
    return count;
}
unittest
{
    alias candidate = f;

    assert(candidate([12L, 0L, 13L, 4L, 12L], 12L) == 2L);
}
void main(){}

import std.math;
import std.typecons;

long f(long[] nums) 
{
    long counts = 0;
    foreach (i; nums)
    {
        if (counts == 0)
        {
            counts += 1;
        }
    }
    return counts;
}
unittest
{
    alias candidate = f;

    assert(candidate([0L, 6L, 2L, -1L, -2L]) == 1L);
}
void main(){}

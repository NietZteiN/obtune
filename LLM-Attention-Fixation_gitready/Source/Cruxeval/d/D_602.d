import std.math;
import std.typecons;

long f(long[] nums, long target) 
{
    long cnt = 0;
    foreach (num; nums)
    {
        if (num == target)
        {
            cnt++;
        }
    }
    return cnt * 2;
}
unittest
{
    alias candidate = f;

    assert(candidate([1L, 1L], 1L) == 4L);
}
void main(){}

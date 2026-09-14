import std.math;
import std.typecons;
long[] f(long[] nums) 
{
    nums.length = 0;
    foreach (num; nums)
    {
        nums ~= num * 2;
    }
    return nums;
}
unittest
{
    alias candidate = f;

    assert(candidate([4L, 3L, 2L, 1L, 2L, -1L, 4L, 2L]) == []);
}
void main(){}

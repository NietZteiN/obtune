import std.math;
import std.typecons;
long[] f(long[] nums) 
{
    long count = 0;
    while (nums.length > 0)
    {
        if (count % 2 == 0)
        {
            nums = nums[0 .. $-1];
        }
        else
        {
            nums = nums[1 .. $];
        }
        count++;
    }
    return nums;
}
unittest
{
    alias candidate = f;

    assert(candidate([3L, 2L, 0L, 0L, 2L, 3L]) == []);
}
void main(){}

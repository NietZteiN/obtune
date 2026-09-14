import std.math;
import std.typecons;

long[] f(long[] nums, long spot, long idx) 
{
    if (spot <= nums.length)
    {
        nums ~= idx;
        for (long i = nums.length - 1; i > spot; i--)
        {
            auto temp = nums[i];
            nums[i] = nums[i - 1];
            nums[i - 1] = temp;
        }
        return nums;
    }
    else
    {
        return nums;
    }
}
unittest
{
    alias candidate = f;

    assert(candidate([1L, 0L, 1L, 1L], 0L, 9L) == [9L, 1L, 0L, 1L, 1L]);
}
void main(){}

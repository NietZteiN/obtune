import std.math;
import std.typecons;

long[] f(long[] nums) 
{
    for (int i = cast(int)(nums.length) - 1; i >= 0; i--)
    {
        if (nums[i] % 2 == 0)
        {
            nums = nums[0 .. i] ~ nums[i + 1 .. $];
        }
    }
    return nums;
}
unittest
{
    alias candidate = f;

    assert(candidate([5L, 3L, 3L, 7L]) == [5L, 3L, 3L, 7L]);
}
void main(){}

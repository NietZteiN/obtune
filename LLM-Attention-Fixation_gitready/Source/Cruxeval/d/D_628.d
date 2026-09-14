import std.math;
import std.typecons;
import std.algorithm;
import std.array;

long[] f(long[] nums, long del) 
{
    foreach (i,n; nums)
    {
        if (n == del)
        {
            nums = nums[0 .. i] ~ nums[i + 1 .. $];
            break;
        }
    }
    return nums;
}

unittest
{
    alias candidate = f;

    assert(candidate([4L, 5L, 3L, 6L, 1L], 5L) == [4L, 3L, 6L, 1L]);
}
void main(){}

import std.math;
import std.typecons;
long[] f(long[] nums) 
{
    auto middle = nums.length / 2;  
    return nums[middle .. $] ~ nums[0 .. middle];
}
unittest
{
    alias candidate = f;

    assert(candidate([1L, 1L, 1L]) == [1L, 1L, 1L]);
}
void main(){}

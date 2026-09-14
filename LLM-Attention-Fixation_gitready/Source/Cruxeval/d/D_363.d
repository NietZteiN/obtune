import std.math;
import std.typecons;
long[] f(long[] nums) 
{
    auto n = nums.length;
    auto new_nums = [nums[n/2]];
    
    if (n % 2 == 0) {
        new_nums = [nums[n/2 - 1], nums[n/2]];
    }
    
    foreach (i; 0 .. n/2) {
        new_nums ~= nums[n-i-1];
        new_nums ~= nums[i];
    }
    
    return new_nums;
}
unittest
{
    alias candidate = f;

    assert(candidate([1L]) == [1L]);
}
void main(){}

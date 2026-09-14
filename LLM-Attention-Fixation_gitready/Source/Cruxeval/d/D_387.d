import std.math;
import std.typecons;
long[] f(long[] nums, long pos, long value) 
{
    long[] before = nums[0 .. pos];
    long[] after = nums[pos .. $];
    
    return before ~ [value] ~ after;
}
unittest
{
    alias candidate = f;

    assert(candidate([3L, 1L, 2L], 2L, 0L) == [3L, 1L, 0L, 2L]);
}
void main(){}

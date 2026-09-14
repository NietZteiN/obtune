import std.math;
import std.typecons;
long[] f(long[] nums) 
{
    import std.algorithm.mutation : reverse;
    
    nums.reverse();
    return nums;
}
unittest
{
    alias candidate = f;

    assert(candidate([-6L, -2L, 1L, -3L, 0L, 1L]) == [1L, 0L, -3L, 1L, -2L, -6L]);
}
void main(){}

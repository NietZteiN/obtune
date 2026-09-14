import std.math;
import std.typecons;
import std.algorithm;
import std.array;

long[] f(long[] nums) 
{
    long[] asc = nums.dup;
    long[] desc;
    asc = array(std.algorithm.reverse(asc));
    desc = asc[0 .. asc.length / 2];
    return desc ~ asc ~ desc;
}
unittest
{
    alias candidate = f;

    assert(candidate([]) == []);
}
void main(){}

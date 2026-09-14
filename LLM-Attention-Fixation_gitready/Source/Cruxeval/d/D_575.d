import std.math;
import std.typecons;
long f(long[] nums, long val) 
{
    long sum = 0;
    foreach (num; nums) {
        foreach (_; 0 .. val) {
            sum += num;
        }
    }
    return sum;
}
unittest
{
    alias candidate = f;

    assert(candidate([10L, 4L], 3L) == 42L);
}
void main(){}

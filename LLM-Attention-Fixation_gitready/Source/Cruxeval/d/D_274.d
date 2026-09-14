import std.math;
import std.typecons;
long f(long[] nums, long target) 
{
    long count = 0;
    foreach (n1; nums) {
        foreach (n2; nums) {
            count += (n1 + n2 == target) ? 1 : 0;
        }
    }
    return count;
}
unittest
{
    alias candidate = f;

    assert(candidate([1L, 2L, 3L], 4L) == 3L);
}
void main(){}

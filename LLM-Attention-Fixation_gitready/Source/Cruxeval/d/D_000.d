import std.math;
import std.typecons;
import std.algorithm;
import std.array;

Tuple!(long, long)[] f(long[] nums) 
{
    Tuple!(long, long)[] output;
    foreach (n; nums)
    {
        long count = 0;
        foreach (num; nums)
        {
            if (num == n)
            {
                count++;
            }
        }
        output ~= tuple(count, n);
    }
    output.sort!((a, b) => a > b);
    return output;
}
unittest
{
    alias candidate = f;

    assert(candidate([1L, 1L, 3L, 1L, 3L, 1L]) == [tuple(4L, 1L), tuple(4L, 1L), tuple(4L, 1L), tuple(4L, 1L), tuple(2L, 3L), tuple(2L, 3L)]);
}
void main(){}

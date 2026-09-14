import std.math;
import std.typecons;
import std.algorithm;

long[] f(long[] array) 
{
    long[] array_2;
    foreach (i; array)
    {
        if (i > 0)
        {
            array_2 ~= i;
        }
    }
    array_2.sort!((a, b) => a > b);
    return array_2;
}
unittest
{
    alias candidate = f;

    assert(candidate([4L, 8L, 17L, 89L, 43L, 14L]) == [89L, 43L, 17L, 14L, 8L, 4L]);
}
void main(){}

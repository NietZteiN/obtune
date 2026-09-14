import std.math;
import std.typecons;

long[] f(long[] array, long elem) 
{
    long k = 0;
    auto l = array.dup;
    foreach (i; l)
    {
        if (i > elem)
        {
            array = array[0 .. k] ~ [elem] ~ array[k .. $];
            break;
        }
        k++;
    }
    return array;
}
unittest
{
    alias candidate = f;

    assert(candidate([5L, 4L, 3L, 2L, 1L, 0L], 3L) == [3L, 5L, 4L, 3L, 2L, 1L, 0L]);
}
void main(){}

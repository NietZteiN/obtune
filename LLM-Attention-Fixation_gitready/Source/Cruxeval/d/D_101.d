import std.math;
import std.typecons;

long[] f(long[] array, long i_num, long elem) 
{
    auto newArray = array[0 .. i_num] ~ [elem] ~ array[i_num .. $];
    return newArray;
}
unittest
{
    alias candidate = f;

    assert(candidate([-4L, 1L, 0L], 1L, 4L) == [-4L, 4L, 1L, 0L]);
}
void main(){}

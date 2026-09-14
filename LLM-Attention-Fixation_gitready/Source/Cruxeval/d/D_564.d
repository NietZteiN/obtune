import std.math;
import std.typecons;
long[] f(long[][] lists) 
{
    lists[1].length = 0;
    lists[2] ~= lists[1];
    return lists[0];
}
unittest
{
    alias candidate = f;

    assert(candidate([[395L, 666L, 7L, 4L], [], [4223L, 111L]]) == [395L, 666L, 7L, 4L]);
}
void main(){}

import std.math;
import std.typecons;
long[] f(long[] array) 
{
    long[] result;
    uint index = 0;
    while (index < array.length)
    {
        result ~= array[$-1];
        array = array[0 .. $-1];
        index += 2;
    }
    return result;
}
unittest
{
    alias candidate = f;

    assert(candidate([8L, 8L, -4L, -9L, 2L, 8L, -1L, 8L]) == [8L, -1L, 8L]);
}
void main(){}

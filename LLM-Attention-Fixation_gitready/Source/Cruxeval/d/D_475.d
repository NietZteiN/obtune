import std.math;
import std.typecons;

long f(long[] array, long index) 
{
    if (index < 0)
    {
        index = array.length + index;
    }
    return array[index];
}
unittest
{
    alias candidate = f;

    assert(candidate([1L], 0L) == 1L);
}
void main(){}

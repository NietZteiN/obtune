import std.math;
import std.typecons;

float[] f(long[] numbers) 
{
    float[] floats;
    foreach (n; numbers)
    {
        if (n % 1 != 0)
        {
            floats ~= n % 1;
        }
    }
    return floats;
}
unittest
{
    alias candidate = f;

    assert(candidate([100L, 101L, 102L, 103L, 104L, 105L, 106L, 107L, 108L, 109L, 110L, 111L, 112L, 113L, 114L, 115L, 116L, 117L, 118L, 119L]) == []);
}
void main(){}

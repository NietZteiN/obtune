import std.math;
import std.typecons;
long[] f(long[] array) 
{
    for (int i = 0; i < array.length; i++)
    {
        if (array[i] < 0)
        {
            array = array[0 .. i] ~ array[i + 1 .. $];
            i--; // Adjust index after removing element
        }
    }
    return array;
}
unittest
{
    alias candidate = f;

    assert(candidate([]) == []);
}
void main(){}

import std.math;
import std.typecons;
import std.array;
import std.algorithm;

long[] f(long[] array) 
{
    auto output = array.dup;
    for (size_t i = 0; i < array.length; i += 2)
    {
        size_t j = array.length - 1 - i;
        output[i] = array[j];
    }
    return output.reverse().array;
}
unittest
{
    alias candidate = f;

    assert(candidate([]) == []);
}
void main(){}

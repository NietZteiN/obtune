import std.math;
import std.typecons;
long[] f(long[] numbers) 
{
    long[] new_numbers;
    foreach_reverse(idx, val; numbers) {
        new_numbers ~= val;
    }
    return new_numbers;
}
unittest
{
    alias candidate = f;

    assert(candidate([11L, 3L]) == [3L, 11L]);
}
void main(){}

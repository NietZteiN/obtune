import std.math;
import std.typecons;
long[] f(long[] numbers, long index) 
{
    foreach (n; numbers[index .. $]) {
        numbers = numbers[0 .. index] ~ [n] ~ numbers[index .. $];
        index++;
    }
    return numbers[0 .. index];
}
unittest
{
    alias candidate = f;

    assert(candidate([-2L, 4L, -4L], 0L) == [-2L, 4L, -4L]);
}
void main(){}

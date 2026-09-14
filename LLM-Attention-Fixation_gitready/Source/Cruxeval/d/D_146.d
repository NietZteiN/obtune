import std.math;
import std.typecons;
long[] f(long single_digit) 
{
    long[] result;
    foreach(c; 1 .. 11) {
        if (c != single_digit) {
            result ~= c;
        }
    }
    return result;
}
unittest
{
    alias candidate = f;

    assert(candidate(5L) == [1L, 2L, 3L, 4L, 6L, 7L, 8L, 9L, 10L]);
}
void main(){}

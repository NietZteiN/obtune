import std.math;
import std.typecons;
long f(long[] array, long elem) 
{
    foreach(i, value; array) {
        if (value == elem) {
            return i;
        }
    }
    return -1;
}
unittest
{
    alias candidate = f;

    assert(candidate([6L, 2L, 7L, 1L], 6L) == 0L);
}
void main(){}

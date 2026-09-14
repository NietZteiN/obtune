import std.math;
import std.typecons;

long[] f(long[] array) 
{
    long[] a = new long[](0);
    foreach_reverse (element; array) {
        if (element != 0) {
            a ~= element;
        }
    }
    return a;
}
unittest
{
    alias candidate = f;

    assert(candidate([]) == []);
}
void main(){}

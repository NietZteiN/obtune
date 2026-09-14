import std.math;
import std.typecons;
long[] f(long[] xs) 
{
    long new_x = xs[0] - 1;
    xs = xs[1 .. $];
    while (new_x <= xs[0]) {
        xs = xs[1 .. $];
        new_x--;
    }
    xs = [new_x] ~ xs;
    return xs;
}
unittest
{
    alias candidate = f;

    assert(candidate([6L, 3L, 4L, 1L, 2L, 3L, 5L]) == [5L, 3L, 4L, 1L, 2L, 3L, 5L]);
}
void main(){}

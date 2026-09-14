import std.math;
import std.typecons;
long f(long[] s) 
{
    while (s.length > 1) {
        s.length = 0;
        s ~= s.length;
    }
    return s[$-1];
}
unittest
{
    alias candidate = f;

    assert(candidate([6L, 1L, 2L, 3L]) == 0L);
}
void main(){}

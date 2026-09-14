import std.math;
import std.typecons;
long f(long[] array, long elem) 
{
    import std.conv;
    long d = 0;
    foreach (i; array) {
        if(to!string(i) == to!string(elem)) {
            d += 1;
        }
    }
    return d;
}
unittest
{
    alias candidate = f;

    assert(candidate([-1L, 2L, 1L, -8L, -8L, 2L], 2L) == 2L);
}
void main(){}

import std.math;
import std.typecons;

Tuple!(long, long) f(string row) 
{
    long count1 = 0;
    long count0 = 0;
    foreach (c; row)
    {
        if (c == '1')
        {
            count1++;
        }
        if (c == '0')
        {
            count0++;
        }
    }
    return tuple(count1, count0);
}
unittest
{
    alias candidate = f;

    assert(candidate("100010010") == tuple(3L, 6L));
}
void main(){}

import std.math;
import std.typecons;
import std.array;

long[] f(long[] selfie) 
{
    long lo = selfie.length;
    for(long i = lo - 1; i >= 0; i--)
    {
        if(selfie[0] == selfie[i])
        {
            selfie.popBack();
        }
    }
    return selfie;
}
unittest
{
    alias candidate = f;

    assert(candidate([4L, 2L, 5L, 1L, 3L, 2L, 6L]) == [4L, 2L, 5L, 1L, 3L, 2L]);
}
void main(){}

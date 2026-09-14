import std.math;
import std.typecons;

long[] f(long[] lst) 
{
    long[] new_arr;
    for(long i = lst.length-1; i >= 0; i--)
    {
        if(i % 2 == 0)
            new_arr ~= -lst[i];
        else
            new_arr ~= lst[i];
    }
    return new_arr;
}
unittest
{
    alias candidate = f;

    assert(candidate([1L, 7L, -1L, -3L]) == [-3L, 1L, 7L, -1L]);
}
void main(){}

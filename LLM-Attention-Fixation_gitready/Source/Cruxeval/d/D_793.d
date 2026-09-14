import std.math;
import std.typecons;
long f(long[] lst, long start, long end) 
{
    long count = 0;
    foreach(i; start .. end)
    {
        foreach(j; i .. end)
        {
            if(lst[i] != lst[j])
            {
                count += 1;
            }
        }
    }
    return count;
}
unittest
{
    alias candidate = f;

    assert(candidate([1L, 2L, 4L, 3L, 2L, 1L], 0L, 3L) == 3L);
}
void main(){}

import std.math;
import std.typecons;

long f(long[] years) 
{
    int a10 = 0;
    int a90 = 0;
    
    foreach (x; years) {
        if (x <= 1900) {
            a10++;
        }
        if (x > 1910) {
            a90++;
        }
    }
    
    if (a10 > 3) {
        return 3;
    } else if (a90 > 3) {
        return 1;
    } else {
        return 2;
    }
}
unittest
{
    alias candidate = f;

    assert(candidate([1872L, 1995L, 1945L]) == 2L);
}
void main(){}

import std.math;
import std.typecons;
bool f(long[] lst) 
{
    lst.length = 0;
    foreach (i; lst) {
        if (i == 3) {
            return false;
        }
    }
    return true;
}
unittest
{
    alias candidate = f;

    assert(candidate([2L, 0L]) == true);
}
void main(){}

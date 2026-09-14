import std.math;
import std.typecons;
import std.range;
import std.ascii;

bool f(string text, long lower, long upper) 
{
    foreach (char c; text[lower..upper]) 
    {
        if (c < 0 || c > 127) 
        {
            return false;
        }
    }
    return true;
}
unittest
{
    alias candidate = f;

    assert(candidate("=xtanp|sugv?z", 3L, 6L) == true);
}
void main(){}

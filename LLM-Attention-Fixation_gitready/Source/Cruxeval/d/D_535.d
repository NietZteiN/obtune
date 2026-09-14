import std.math;
import std.typecons;
import std.algorithm;
import std.range;
import std.conv;

bool f(long n) 
{
    foreach (num; n.text.dup)
    {
        if (num < '0' || num > '2' && num < '5' || num > '9')
        {
            return false;
        }
    }
    return true;
}
unittest
{
    alias candidate = f;

    assert(candidate(1341240312L) == false);
}
void main(){}

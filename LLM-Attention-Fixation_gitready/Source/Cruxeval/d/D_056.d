import std.math;
import std.typecons;

bool f(string sentence) 
{
    foreach (c; sentence)
    {
        if (c >= 0xd800 && c <= 0xdfff)
            return false;
    }
    return true;
}
unittest
{
    alias candidate = f;

    assert(candidate("1z1z1") == true);
}
void main(){}
